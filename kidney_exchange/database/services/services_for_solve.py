from typing import List, Dict, Tuple

from kidney_exchange.database.services.patient_service import get_donor_from_db_id, get_recipient_from_db_id, \
    get_all_patients, get_patient_from_db_id
from kidney_exchange.database.sql_alchemy_schema import PairingResultModel, PairingResultPatientModel
from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


def get_pairing_result_for_config(config_id: int) -> List[PairingResultModel]:
    return PairingResultModel.query.filter(PairingResultModel.config_id == config_id).all()


def get_patients_for_pairing_result(pairing_result_id: int) -> List[PairingResultPatientModel]:
    return PairingResultPatientModel.query.filter(
        PairingResultPatientModel.pairing_result_id == pairing_result_id).all()


def db_matchings_to_matching_list(json_matchings: Dict[str, List[Dict[str, List[Dict[str, int]]]]]) -> List[Matching]:
    patients = get_all_patients()
    patients_dict = {patient.id: get_patient_from_db_id(patient.id) for patient in patients}

    return [Matching([(patients_dict[donor_recipient_ids['donor']],
                       patients_dict[donor_recipient_ids['recipient']])
                      for donor_recipient_ids in json_matching['donors_recipients']
                      ]) for json_matching in json_matchings["matchings"]]


def get_patients_from_ids(donor_id: int, recipient_id: int) -> Tuple[Donor, Recipient]:
    return get_donor_from_db_id(donor_id), get_recipient_from_db_id(recipient_id)


