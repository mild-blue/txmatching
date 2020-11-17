from typing import List

from txmatching.patients.patient import Patient
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.enums import HLAGroups, MatchTypes
from txmatching.utils.hla_system.compatibility_index import \
    compatibility_index_detailed


def get_matching_hla_typing(donor: Patient, recipient: Patient) -> List[str]:
    """
    Gets matching HLA typings of donor and recipient.
    :param donor:
    :param recipient:
    :return: List of same HLA typings of donor and recipient.
    """
    scores = compatibility_index_detailed(donor.parameters.hla_typing,
                                          recipient.parameters.hla_typing)
    return list({match.hla_code for ci_detail_group in scores for match in ci_detail_group.recipient_matches
                 if match.match_type != MatchTypes.NONE})


def calculate_compatibility_index_for_group(donor: Patient, recipient: Patient, hla_group: HLAGroups) -> float:
    """
    Calculates antigen score of donor and recipient of particular HLA type.
    :param donor:
    :param recipient:
    :param hla_group:
    :return: Score value.
    """

    scores = compatibility_index_detailed(donor.parameters.hla_typing,
                                          recipient.parameters.hla_typing)
    return next(group_ci_detailed.group_compatibility_index for group_ci_detailed in scores if
                group_ci_detailed.hla_group == hla_group)


def get_count_of_transplants(matching: MatchingWithScore) -> int:
    """
    Gets count of transplants of matching, i.e., sum of all recipient pairs in all matching rounds.
    :param matching:
    :return: Count of transplants.
    """
    count_of_transplants = 0
    for matching_round in matching.get_rounds():
        count_of_transplants += len(matching_round.donor_recipient_pairs)
    return count_of_transplants
