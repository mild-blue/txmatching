from typing import List, Tuple, Optional

from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import PatientAcceptableBloodModel, PatientModel, PatientPairModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.recipient import Recipient


def medical_id_to_id(medical_id: str) -> Optional[int]:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 0:
        return None
    elif len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f"There has to be 1 patient per medical id, but {len(patients_with_id)} "
                         f"were found for patient with medical id {medical_id}")


def create_patient_model_from_patient(patient: Patient) -> PatientModel:
    patient_model = PatientModel(
        medical_id=patient.medical_id,
        country=patient.params.country_code,
        blood=patient.params.blood_group,
        typization={},  # TODO https://trello.com/c/1ynqm5tA,
        luminex={},  # TODO https://trello.com/c/1ynqm5tA,
        active=True
    )
    if type(patient) == Recipient:
        patient_model.acceptable_blood = [PatientAcceptableBloodModel(blood_type=blood)
                                          for blood in patient.params.acceptable_blood_groups]
        patient_model.patient_type = 'RECIPIENT'
        patient_model.patient_pairs = [PatientPairModel(donor_id=medical_id_to_id(patient.related_donor.medical_id))]

    elif type(patient) == Donor:
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
        patients_to_add.append(patient)

    PatientModel.query.filter(PatientModel.id.in_(existing_patient_ids)).delete('fetch')
    db.session.add_all(patients_to_add)
    db.session.commit()


def save_patients(donors_recipients: Tuple[List[Donor], List[Recipient]]):
    patient_models = [create_patient_model_from_patient(patient)
                      for donor_recipient in donors_recipients for patient in donor_recipient]
    save_patient_models(patient_models)
