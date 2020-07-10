from typing import List, Tuple, Optional

from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import PatientAcceptableBloodModel, PatientModel, PatientPairModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.recipient import Recipient

ACCEPTABLE_BLOOD_GROUPS_DICT = {
    "A": ["0", "A", "AB"],
    "0": ["0"],
    "B": ["0", "B", "AB"],
    "AB": ["0", "A", "B", "AB"],
}


def medical_id_to_id(medical_id: str) -> Optional[int]:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 0:
        return None
    elif len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f"There has to be 1 patient per medical id, but {len(patients_with_id)} "
                         f"were found for patient with medical id {medical_id}")


def create_patient_model_from_patient(patient: Patient, patient_type: str) -> PatientModel:
    acceptable_blood_groups = patient.params.acceptable_blood_groups
    if patient.params.acceptable_blood_groups is None:
        acceptable_blood_groups = ACCEPTABLE_BLOOD_GROUPS_DICT[str(patient.params.blood_group)]
    acceptable_blood_groups = [PatientAcceptableBloodModel(blood_type=blood) for blood in acceptable_blood_groups]
    patient_model = PatientModel(
        medical_id=patient.medical_id,
        country=patient.params.country_code,
        patient_type=patient_type,
        blood=patient.params.blood_group,
        typization={},
        luminex={},
        acceptable_blood=acceptable_blood_groups,
        active=True
    )
    return patient_model


def create_recipient_model_from_recipient(recipient: Recipient):
    patient_model = create_patient_model_from_patient(recipient, 'RECIPIENT')

    patient_model.patient_pairs = [PatientPairModel(donor_id=medical_id_to_id(recipient.related_donor.medical_id))]
    return patient_model


def save_patient_models(patient_models: List[PatientModel]):
    existing_patient_ids = [maybe_patient_id for maybe_patient_id in
                            [medical_id_to_id(patient.medical_id) for patient in patient_models]]
    patients_to_add = []
    for patient, maybe_patient_id in zip(patient_models, existing_patient_ids):
        if maybe_patient_id is not None:
            patient.id = maybe_patient_id
        patients_to_add.append(patient)

    PatientModel.query.filter(PatientModel.id.in_(existing_patient_ids)).delete('fetch')
    db.session.add_all(patients_to_add)
    db.session.commit()


def save_patients(donors_recipients: Tuple[List[Donor], List[Recipient]]):
    donor_models = [create_patient_model_from_patient(donor, 'DONOR') for donor in donors_recipients[0]]
    save_patient_models(donor_models)

    recipient_models = [create_recipient_model_from_recipient(recipient) for recipient in donors_recipients[1]]
    save_patient_models(recipient_models)



