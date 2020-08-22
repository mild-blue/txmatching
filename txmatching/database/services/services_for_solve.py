from typing import List, Dict, Union

from txmatching.database.sql_alchemy_schema import PairingResultModel, PairingResultPatientModel
from txmatching.patients.patient import Patient
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


def get_pairing_result_for_config(config_id: int) -> List[PairingResultModel]:
    return PairingResultModel.query.filter(PairingResultModel.config_id == config_id).all()


def get_patients_for_pairing_result(pairing_result_id: int) -> List[PairingResultPatientModel]:
    return PairingResultPatientModel.query.filter(
        PairingResultPatientModel.pairing_result_id == pairing_result_id).all()


def db_matchings_to_matching_list(
        json_matchings: Dict[str, List[Dict[str, Union[float, List[Dict[str, int]]]]]],
        patients_dict: Dict[int, Patient],
) -> List[MatchingWithScore]:
    return [MatchingWithScore([(patients_dict[donor_recipient_ids['donor']],
                                patients_dict[donor_recipient_ids['recipient']])
                               for donor_recipient_ids in json_matching['donors_recipients']
                               ], json_matching["score"]) for json_matching in json_matchings["matchings"]]
