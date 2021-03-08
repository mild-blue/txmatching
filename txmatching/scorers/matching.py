from txmatching.solvers.matching.matching_with_score import MatchingWithScore


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
