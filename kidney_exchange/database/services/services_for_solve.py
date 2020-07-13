from typing import List, Dict, Tuple, Iterable

from kidney_exchange.database.sql_alchemy_schema import PairingResultModel, PairingResultPatientModel, \
    PatientModel, PatientPairModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.patient_parameters import PatientParameters, HLAAntigens, HLAAntibodies
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


def get_pairing_result_for_config(config_id: int) -> List[PairingResultModel]:
    return PairingResultModel.query.filter(PairingResultModel.config_id == config_id).all()


def get_patients_for_pairing_result(pairing_result_id: int) -> List[PairingResultPatientModel]:
    return PairingResultPatientModel.query.filter(
        PairingResultPatientModel.pairing_result_id == pairing_result_id).all()


def db_matching_to_matching(json_matchings: List[List[Dict[str, int]]]) -> List[Matching]:
    return [Matching([get_patients_from_ids(donor_recipient_ids['donor'], donor_recipient_ids['recipient'])
                      for donor_recipient_ids in json_matching
                      ]) for json_matching in json_matchings]


def get_patients_from_ids(donor_id: int, recipient_id: int) -> Tuple[Donor, Recipient]:
    return get_donor_from_db(donor_id), get_recipient_from_db(recipient_id)


def get_patient_from_model(patient_id: int) -> Patient:
    patient_model = PatientModel.query.get(patient_id)
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            blood_group=patient_model.blood,
            acceptable_blood_groups=patient_model.acceptable_blood,
            country_code=patient_model.country,
            hla_antigens=HLAAntigens(**patient_model.hla_antigens),
            hla_antibodies=HLAAntibodies(**patient_model.hla_antibodies)
        ))


def get_donor_from_db(patient_id: int) -> Donor:
    donor = get_patient_from_model(patient_id)
    return Donor(donor.db_id, donor.medical_id, donor.parameters)


def get_recipient_from_db(patient_id: int):
    recipient = get_patient_from_model(patient_id)
    related_donors = PatientPairModel.query.filter(PatientPairModel.recipient_id == patient_id).all()
    if len(related_donors) == 1:
        don_id = related_donors[0].donor_id
    else:
        raise ValueError(f"There has to be 1 donor per recipient, but {len(related_donors)} "
                         f"were found for recipient with db_id {patient_id} and medical id {recipient.medical_id}")
    return Recipient(recipient.db_id, recipient.medical_id, recipient.parameters,
                     get_donor_from_db(don_id))


def get_all_patients() -> Iterable[PatientModel]:
    return PatientModel.query.filter(PatientModel.active).all()
