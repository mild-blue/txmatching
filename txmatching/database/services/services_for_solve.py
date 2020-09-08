from typing import List, Dict, Union

from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.patients.patient import Recipient, Donor
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


def get_pairing_result_for_config(config_id: int) -> List[PairingResultModel]:
    return PairingResultModel.query.filter(PairingResultModel.config_id == config_id).all()


def db_matchings_to_matching_list(
        json_matchings: Dict[str, List[Dict[str, Union[float, List[Dict[str, int]]]]]],
        donors_dict: Dict[int, Donor], recipients_dict: Dict[int, Recipient],
) -> List[MatchingWithScore]:
    return [MatchingWithScore([(donors_dict[donor_recipient_ids['donor']],
                                recipients_dict[donor_recipient_ids['recipient']])
                               for donor_recipient_ids in json_matching['donors_recipients']
                               ], json_matching["score"]) for json_matching in json_matchings["matchings"]]
