import dataclasses
from typing import List, Tuple, Optional, Iterable

from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import PatientAcceptableBloodModel, PatientModel, PatientPairModel, \
    PairingResultPatientModel
from kidney_exchange.patients.donor import DonorDto, Donor
from kidney_exchange.patients.patient import PatientDto, Patient
from kidney_exchange.patients.patient_parameters import PatientParameters, HLAAntigens, HLAAntibodies
from kidney_exchange.patients.recipient import RecipientDto, Recipient


def medical_id_to_db_id(medical_id: str) -> Optional[int]:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 0:
        return None
    elif len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f"There has to be 1 patient per medical id, but {len(patients_with_id)} "
                         f"were found for patient with medical id {medical_id}")


def db_id_to_medical_id(db_id: int) -> str:
    return PatientModel.query.get(db_id).medical_id


def patient_dto_to_patient_model(patient: PatientDto) -> PatientModel:
    patient_model = PatientModel(
        medical_id=patient.medical_id,
        country=patient.parameters.country_code,
        blood=patient.parameters.blood_group,
        hla_antigens=dataclasses.asdict(patient.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(patient.parameters.hla_antibodies),
        active=True
    )
    if type(patient) == RecipientDto:
        patient_model.acceptable_blood = [PatientAcceptableBloodModel(blood_type=blood)
                                          for blood in patient.parameters.acceptable_blood_groups]
        patient_model.patient_type = 'RECIPIENT'
        patient_model.patient_pairs = [
            PatientPairModel(donor_id=medical_id_to_db_id(patient.related_donor.medical_id))]

    elif type(patient) == DonorDto:
        patient_model.patient_type = 'DONOR'
    else:
        raise TypeError(f"Unexpected patient type {type(patient)}")

    return patient_model


def save_patient_models(patient_models: List[PatientModel]):
    existing_patient_ids = [medical_id_to_db_id(patient.medical_id) for patient in patient_models]
    patients_to_add = []
    for patient, maybe_patient_id in zip(patient_models, existing_patient_ids):
        if maybe_patient_id is not None:
            patient.id = maybe_patient_id
            patient.patient_results = [PairingResultPatientModel(
                patient_id=result.id,
                pairing_result_id=result.pairing_result_id
            ) for result in PatientModel.query.get(maybe_patient_id).patient_results]
        patients_to_add.append(patient)

    PatientModel.query.filter(PatientModel.id.in_(existing_patient_ids)).delete('fetch')
    db.session.add_all(patients_to_add)
    db.session.commit()


def save_patients(donors_recipients: Tuple[List[DonorDto], List[RecipientDto]]):
    donor_models = [patient_dto_to_patient_model(donor) for donor in donors_recipients[0]]
    save_patient_models(donor_models)

    recipient_models = [patient_dto_to_patient_model(recipient) for recipient in donors_recipients[1]]
    save_patient_models(recipient_models)


def _get_base_patient_from_patient_model(patient_model: PatientModel) -> Patient:
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            blood_group=patient_model.blood,
            acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                     patient_model.acceptable_blood],
            country_code=patient_model.country,
            hla_antigens=HLAAntigens(**patient_model.hla_antigens),
            hla_antibodies=HLAAntibodies(**patient_model.hla_antibodies)
        ))


def get_patient_from_db_id(db_id: int):
    patient_model = PatientModel.query.get(db_id)
    if patient_model.patient_type == 'RECIPIENT':
        recipient = _get_base_patient_from_patient_model(patient_model)
        related_donors = PatientPairModel.query.filter(PatientPairModel.recipient_id == db_id).all()
        if len(related_donors) == 1:
            don_id = related_donors[0].donor_id
        else:
            raise ValueError(f"There has to be 1 donor per recipient, but {len(related_donors)} "
                             f"were found for recipient with db_id {db_id} and medical id {recipient.medical_id}")
        return Recipient(recipient.db_id, recipient.medical_id, recipient.parameters,
                         get_donor_from_db_id(don_id))
    if patient_model.patient_type == 'DONOR':
        donor = _get_base_patient_from_patient_model(patient_model)
        return Donor(donor.db_id, donor.medical_id, donor.parameters)


def get_donor_from_db_id(db_id: int) -> Donor:
    donor = get_patient_from_db_id(db_id)
    if type(donor) != Donor:
        raise ValueError()
    return donor


def get_recipient_from_db_id(db_id: int) -> Recipient:
    recipient = get_patient_from_db_id(db_id)
    if type(recipient) != Recipient:
        raise ValueError()
    return recipient


def get_all_patients() -> Iterable[PatientModel]:
    return PatientModel.query.filter(PatientModel.active).all()


def get_donors_recipients_from_db() -> Tuple[List[Donor], List[Recipient]]:
    patients = get_all_patients()
    donors = [get_donor_from_db_id(donor.id) for donor in patients if donor.patient_type == 'DONOR']
    recipients = [get_recipient_from_db_id(recipient.id) for recipient in patients if
                  recipient.patient_type == 'RECIPIENT']
    return donors, recipients
