import dataclasses
from typing import List, Tuple, Optional

from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import PatientAcceptableBloodModel, PatientModel, PatientPairModel, \
    PairingResultPatientModel
from kidney_exchange.patients.donor import DonorDto
from kidney_exchange.patients.patient import PatientDto
from kidney_exchange.patients.recipient import RecipientDto


def medical_id_to_id(medical_id: str) -> Optional[int]:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 0:
        return None
    elif len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f"There has to be 1 patient per medical id, but {len(patients_with_id)} "
                         f"were found for patient with medical id {medical_id}")


def id_to_medical_id(id: int) -> str:
    return PatientModel.query.get(id).medical_id


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
            PatientPairModel(donor_id=medical_id_to_id(patient.related_donor.medical_id))]

    elif type(patient) == DonorDto:
        patient_model.patient_type = 'DONOR'
    else:
        raise TypeError(f"Uexpected patient type {type(patient)}")

    return patient_model


def save_patient_models(patient_models: List[PatientModel]):
    existing_patient_ids = [medical_id_to_id(patient.medical_id) for patient in patient_models]
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
