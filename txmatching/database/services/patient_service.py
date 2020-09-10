import dataclasses
from typing import List, Optional, Tuple, Union, Dict

from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorExcelDTO
from txmatching.data_transfer_objects.patients.patient_excel_dto import \
    PatientExcelDTO
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientExcelDTO
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import RecipientAcceptableBloodModel, RecipientModel, DonorModel, \
    PairingResultModel
from txmatching.patients.patient import Patient, DonorType, DonorsRecipients, Recipient, Donor
from txmatching.patients.patient_parameters import (HLAAntibodies,
                                                    HLAAntigens,
                                                    PatientParameters)
from txmatching.patients.patient_types import RecipientDbId


def donor_excel_dto_to_donor_model(patient: PatientExcelDTO, recipient: Optional[RecipientModel]) -> DonorModel:
    maybe_recipient_id = recipient.id if recipient is not None else None
    donor_type = DonorType.DONOR if recipient is not None else DonorType.ALTRUIST
    donor_model = DonorModel(
        medical_id=patient.medical_id,
        country=patient.parameters.country_code,
        blood=patient.parameters.blood_group,
        hla_antigens=dataclasses.asdict(patient.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(patient.parameters.hla_antibodies),
        active=True,
        recipient_id=maybe_recipient_id,
        donor_type=donor_type
    )
    return donor_model


def recipient_excel_dto_to_recipient_model(recipient: RecipientExcelDTO) -> RecipientModel:
    patient_model = RecipientModel(
        medical_id=recipient.medical_id,
        country=recipient.parameters.country_code,
        blood=recipient.parameters.blood_group,
        hla_antigens=dataclasses.asdict(recipient.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(recipient.parameters.hla_antibodies),
        active=True,
        acceptable_blood=[RecipientAcceptableBloodModel(blood_type=blood)
                          for blood in recipient.acceptable_blood_groups]
    )
    return patient_model


def overwrite_patients_by_patients_from_excel(donors_recipients: Tuple[List[DonorExcelDTO], List[RecipientExcelDTO]]):
    RecipientModel.query.delete()
    DonorModel.query.delete()
    PairingResultModel.query.delete()

    maybe_recipient_models = [recipient_excel_dto_to_recipient_model(recipient) if recipient is not None else None for
                              recipient in donors_recipients[1]]
    recipient_models = [recipient_model for recipient_model in maybe_recipient_models if
                        recipient_model is not None]
    db.session.add_all(recipient_models)
    db.session.commit()

    donor_models = [donor_excel_dto_to_donor_model(donor_dto, maybe_recipient_model) for
                    donor_dto, maybe_recipient_model in zip(donors_recipients[0], maybe_recipient_models)]
    db.session.add_all(donor_models)
    db.session.commit()


def _get_base_patient_from_patient_model(patient_model: Union[DonorModel, RecipientModel]) -> Patient:
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            blood_group=patient_model.blood,
            country_code=patient_model.country,
            hla_antigens=HLAAntigens(**patient_model.hla_antigens),
            hla_antibodies=HLAAntibodies(**patient_model.hla_antibodies)
        ))


def _get_donor_from_donor_model(donor_model: DonorModel) -> Donor:
    base_patient = _get_base_patient_from_patient_model(donor_model)

    return Donor(base_patient.db_id,
                 base_patient.medical_id,
                 parameters=base_patient.parameters,
                 donor_type=donor_model.donor_type,
                 related_recipient_db_id=donor_model.recipient_id
                 )


def _get_recipient_from_recipient_model(recipient_model: RecipientModel,
                                        donors_for_recipients_dict: Dict[RecipientDbId, Donor]) -> Recipient:
    base_patient = _get_base_patient_from_patient_model(recipient_model)

    return Recipient(base_patient.db_id,
                     base_patient.medical_id,
                     parameters=base_patient.parameters,
                     related_donor_db_id=donors_for_recipients_dict[base_patient.db_id].db_id,
                     acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                              recipient_model.acceptable_blood],
                     )


def save_recipient(recipient: Recipient) -> int:
    acceptable_blood_models = [RecipientAcceptableBloodModel(blood_type=blood, recipient_id=recipient.db_id) for blood
                               in
                               recipient.acceptable_blood_groups]
    RecipientAcceptableBloodModel.query.filter(RecipientAcceptableBloodModel.recipient_id == recipient.db_id).delete()
    db.session.add_all(acceptable_blood_models)
    RecipientModel.query.filter(RecipientModel.id == recipient.db_id).update({
        "active": True,
        "country": recipient.parameters.country_code,
        "hla_antigens": dataclasses.asdict(recipient.parameters.hla_antigens),
        "hla_antibodies": dataclasses.asdict(recipient.parameters.hla_antibodies),
        "medical_id": recipient.medical_id,
        "blood": recipient.parameters.blood_group,
        "recipient_requirements": dataclasses.asdict(recipient.recipient_requirements)
    })
    db.session.commit()
    return recipient.db_id


def save_donor(donor: Donor) -> int:
    DonorModel.query.filter(DonorModel.id == donor.db_id).update({
        "id": donor.db_id,
        "donor_type": donor.donor_type,
        "country": donor.parameters.country_code,
        "active": True,
        "hla_antigens": dataclasses.asdict(donor.parameters.hla_antigens),
        "hla_antibodies": dataclasses.asdict(donor.parameters.hla_antibodies),
        "medical_id": donor.medical_id,
        "blood": donor.parameters.blood_group,
        "recipient_id": donor.related_recipient_db_id
    })
    db.session.commit()
    return donor.db_id


def get_all_donors_recipients() -> DonorsRecipients:
    active_donors = DonorModel.query.filter(DonorModel.active)
    donors_with_recipients = [(donor_model.recipient_id, _get_donor_from_donor_model(donor_model)) for donor_model
                              in active_donors]

    donors_dict = {donor.db_id: donor for _, donor in donors_with_recipients}
    donors_with_recipients_dict = {k: v for k, v in donors_with_recipients if k is not None}

    active_recipients = RecipientModel.query.filter(RecipientModel.active)
    recipients = {recipient_model.id: _get_recipient_from_recipient_model(recipient_model, donors_with_recipients_dict)
                  for recipient_model in active_recipients}

    return DonorsRecipients(donors_dict, recipients)
