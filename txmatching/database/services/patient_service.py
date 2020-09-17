import dataclasses
import logging
from typing import Dict, List, Optional, Tuple, Union

from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorExcelDTO
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientExcelDTO
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import \
    get_newest_txm_event_db_id
from txmatching.database.sql_alchemy_schema import (
    DonorModel, RecipientAcceptableBloodModel, RecipientModel, TxmEventModel)
from txmatching.patients.patient import (Donor, DonorType, Patient, Recipient,
                                         TxmEvent)
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntigens,
                                                    PatientParameters)
from txmatching.patients.patient_types import RecipientDbId

logger = logging.getLogger(__name__)


def donor_excel_dto_to_donor_model(donor: DonorExcelDTO, recipient: Optional[RecipientModel],
                                   tx_session_db_id: int) -> DonorModel:
    maybe_recipient_id = recipient.id if recipient else None
    donor_type = DonorType.DONOR if recipient else DonorType.ALTRUIST
    donor_model = DonorModel(
        medical_id=donor.medical_id,
        country=donor.parameters.country_code,
        blood=donor.parameters.blood_group,
        hla_antigens=dataclasses.asdict(donor.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(donor.parameters.hla_antibodies),
        active=True,
        recipient_id=maybe_recipient_id,
        donor_type=donor_type,
        txm_event_id=tx_session_db_id
    )
    return donor_model


def recipient_excel_dto_to_recipient_model(recipient: RecipientExcelDTO, tx_session_db_id: int) -> RecipientModel:
    patient_model = RecipientModel(
        medical_id=recipient.medical_id,
        country=recipient.parameters.country_code,
        blood=recipient.parameters.blood_group,
        hla_antigens=dataclasses.asdict(recipient.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(recipient.parameters.hla_antibodies),
        active=True,
        acceptable_blood=[RecipientAcceptableBloodModel(blood_type=blood)
                          for blood in recipient.acceptable_blood_groups],
        txm_event_id=tx_session_db_id
    )
    return patient_model


def save_patients_from_excel_to_empty_txm_event(donors_recipients: Tuple[List[DonorExcelDTO], List[RecipientExcelDTO]],
                                                txm_event_db_id: int):
    txm_event = get_txm_event(txm_event_db_id)
    if len(txm_event.donors_dict) > 0 or len(txm_event.recipients_dict) > 0:
        raise ValueError('Tx session not empty, cannot send patients to database')

    maybe_recipient_models = [recipient_excel_dto_to_recipient_model(recipient, txm_event_db_id)
                              if recipient else None for recipient in donors_recipients[1]]
    recipient_models = [recipient_model for recipient_model in maybe_recipient_models if recipient_model]
    db.session.add_all(recipient_models)
    db.session.commit()

    donor_models = [donor_excel_dto_to_donor_model(donor_dto, maybe_recipient_model, txm_event_db_id) for
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


def update_recipient(recipient: Recipient) -> int:
    acceptable_blood_models = [RecipientAcceptableBloodModel(blood_type=blood, recipient_id=recipient.db_id) for blood
                               in
                               recipient.acceptable_blood_groups]
    RecipientAcceptableBloodModel.query.filter(RecipientAcceptableBloodModel.recipient_id == recipient.db_id).delete()
    db.session.add_all(acceptable_blood_models)
    RecipientModel.query.filter(RecipientModel.id == recipient.db_id).update({
        'active': True,
        'country': recipient.parameters.country_code,
        'hla_antigens': dataclasses.asdict(recipient.parameters.hla_antigens),
        'hla_antibodies': dataclasses.asdict(recipient.parameters.hla_antibodies),
        'medical_id': recipient.medical_id,
        'blood': recipient.parameters.blood_group,
        'recipient_requirements': dataclasses.asdict(recipient.recipient_requirements)
    })
    db.session.commit()
    return recipient.db_id


def update_donor(donor: Donor) -> int:
    DonorModel.query.filter(DonorModel.id == donor.db_id).update({
        'id': donor.db_id,
        'donor_type': donor.donor_type,
        'country': donor.parameters.country_code,
        'active': True,
        'hla_antigens': dataclasses.asdict(donor.parameters.hla_antigens),
        'hla_antibodies': dataclasses.asdict(donor.parameters.hla_antibodies),
        'medical_id': donor.medical_id,
        'blood': donor.parameters.blood_group,
        'recipient_id': donor.related_recipient_db_id
    })
    db.session.commit()
    return donor.db_id


def get_txm_event(txm_event_db_id: Optional[int] = None) -> TxmEvent:
    if not txm_event_db_id:
        txm_event_db_id = get_newest_txm_event_db_id()
    txm_event_model = TxmEventModel.query.get(txm_event_db_id)

    active_donors = txm_event_model.donors
    active_recipients = txm_event_model.recipients
    donors_with_recipients = [(donor_model.recipient_id, _get_donor_from_donor_model(donor_model))
                              for donor_model in active_donors]

    donors_dict = {donor.db_id: donor for _, donor in donors_with_recipients}
    donors_with_recipients_dict = {related_recipient_id: donor for related_recipient_id, donor in donors_with_recipients
                                   if related_recipient_id}

    recipients_dict = {
        recipient_model.id: _get_recipient_from_recipient_model(
            recipient_model, donors_with_recipients_dict)
        for recipient_model in active_recipients}

    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, donors_dict=donors_dict,
                    recipients_dict=recipients_dict)
