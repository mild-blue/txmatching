import dataclasses
from typing import Dict, Iterable, List, Optional, Tuple

from txmatching.data_transfer_objects.patients.donor_dto import DonorDTO
from txmatching.data_transfer_objects.patients.patient_dto import \
    PatientDTO
from txmatching.data_transfer_objects.patients.recipient_dto import \
    RecipientDTO
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import (
    PairingResultPatientModel, PatientAcceptableBloodModel, PatientModel,
    PatientPairModel)
from txmatching.patients.donor import Donor
from txmatching.patients.patient import Patient, PatientType
from txmatching.patients.patient_parameters import (HLAAntibodies,
                                                         HLAAntigens,
                                                         PatientParameters)
from txmatching.patients.recipient import Recipient


def medical_id_to_db_id(medical_id: str) -> Optional[int]:
    patients_with_id = PatientModel.query.filter(PatientModel.medical_id == medical_id).all()
    if len(patients_with_id) == 0:
        return None
    elif len(patients_with_id) == 1:
        return patients_with_id[0].id
    else:
        raise ValueError(f'There has to be 1 patient per medical id, but {len(patients_with_id)} '
                         f'were found for patient with medical id {medical_id}')


def db_id_to_medical_id(db_id: int) -> str:
    return PatientModel.query.get(db_id).medical_id


def patient_dto_to_patient_model(patient: PatientDTO) -> PatientModel:
    patient_model = PatientModel(
        medical_id=patient.medical_id,
        country=patient.parameters.country_code,
        blood=patient.parameters.blood_group,
        hla_antigens=dataclasses.asdict(patient.parameters.hla_antigens),
        hla_antibodies=dataclasses.asdict(patient.parameters.hla_antibodies),
        active=True
    )
    if isinstance(patient, RecipientDTO):
        patient_model.acceptable_blood = [PatientAcceptableBloodModel(blood_type=blood)
                                          for blood in patient.parameters.acceptable_blood_groups]
        patient_model.patient_type = PatientType.RECIPIENT
        patient_model.patient_pairs = [
            PatientPairModel(donor_id=medical_id_to_db_id(patient.related_donor.medical_id))]

    elif isinstance(patient, DonorDTO):
        patient_model.patient_type = PatientType.DONOR
    else:
        raise TypeError(f'Unexpected patient type {type(patient)}')

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


def save_patients(donors_recipients: Tuple[List[DonorDTO], List[RecipientDTO]]):
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


def _get_patient_from_patient_model(patient_model: PatientModel,
                                    patient_models_dict: Dict[int, PatientModel]) -> Patient:
    base_patient = _get_base_patient_from_patient_model(patient_model)
    if patient_model.patient_type.is_recipient_like():
        related_donors = patient_model.patient_pairs
        if len(related_donors) == 1:
            don_id = related_donors[0].donor_id
        else:
            raise ValueError(f'There has to be 1 donor per recipient, but {len(related_donors)} '
                             f'were found for recipient with db_id {base_patient.db_id}'
                             f' and medical id {base_patient.medical_id}')
        return Recipient(base_patient.db_id, base_patient.medical_id, base_patient.parameters,
                         related_donor=_get_patient_from_patient_model(patient_models_dict[don_id],
                                                                       patient_models_dict),
                         patient_type=patient_model.patient_type)

    return Donor(base_patient.db_id, base_patient.medical_id, parameters=base_patient.parameters,
                 patient_type=patient_model.patient_type)


def get_all_patients() -> Iterable[Patient]:
    patient_models_dict = {patient_model.id: patient_model for patient_model in
                           PatientModel.query.filter(PatientModel.active).order_by(PatientModel.id).all()}
    patients = [_get_patient_from_patient_model(patient_model, patient_models_dict) for patient_model in
                patient_models_dict.values()]
    return patients


def get_donors_recipients_from_db() -> Tuple[List[Donor], List[Recipient]]:
    patients = get_all_patients()
    donors = [donor for donor in patients if isinstance(donor, Donor)]
    recipients = [recipient for recipient in patients if isinstance(recipient, Recipient)]
    return donors, recipients
