from txmatching.patients.patient import Patient
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.enums import HLAGroup
from txmatching.utils.hla_system.compatibility_index import \
    get_detailed_compatibility_index


def calculate_compatibility_index_for_group(donor: Patient, recipient: Patient, hla_group: HLAGroup) -> float:
    """
    Calculates antigen score of donor and recipient of particular HLA type.
    :param donor:
    :param recipient:
    :param hla_group:
    :return: Score value.
    """

    scores = get_detailed_compatibility_index(donor.parameters.hla_typing,
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
