from typing import List

from txmatching.patients.patient import Patient
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.enums import HLATypes, HLA_TYPING_BONUS_PER_GENE_CODE_STR


def get_matching_hla_typing(donor: Patient, recipient: Patient) -> List[str]:
    donor_hla_typing = donor.parameters.hla_typing.codes
    recipient_hla_typing = recipient.parameters.hla_typing.codes
    return list(set(donor_hla_typing) & set(recipient_hla_typing))


def calculate_antigen_score(donor: Patient, recipient: Patient, antigen: HLATypes) -> int:
    filtered = list(
        filter(lambda x: x.upper().startswith(antigen.upper()), get_matching_hla_typing(donor, recipient)))
    return len(filtered) * HLA_TYPING_BONUS_PER_GENE_CODE_STR[antigen.upper()]


def get_count_of_transplants(matching: MatchingWithScore) -> int:
    count_of_transplants = 0
    for matching_round in matching.get_rounds():
        count_of_transplants += len(matching_round.donor_recipient_pairs)
    return count_of_transplants
