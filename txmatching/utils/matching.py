from typing import List

from txmatching.patients.patient import Patient
from txmatching.patients.patient_parameters import HLAAntibodies, HLAType
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.enums import HLATypes, HLA_TYPING_BONUS_PER_GENE_CODE_STR


def get_matching_hla_typing(donor: Patient, recipient: Patient) -> List[str]:
    """
    Gets matching HLA typings of donor and recipient.
    :param donor:
    :param recipient:
    :return: List of same HLA typings of donor and recipient.
    """
    donor_hla_typing = donor.parameters.hla_typing.codes
    recipient_hla_typing = recipient.parameters.hla_typing.codes
    return list(set(donor_hla_typing) & set(recipient_hla_typing))


def calculate_antigen_score(donor: Patient, recipient: Patient, antigen: HLATypes) -> int:
    """
    Calculates antigen score of donor and recipient of particular HLA type.
    :param donor:
    :param recipient:
    :param antigen:
    :return: Score value.
    """
    filtered = list(
        filter(lambda x: x.upper().startswith(antigen.upper()), get_matching_hla_typing(donor, recipient)))
    return len(filtered) * HLA_TYPING_BONUS_PER_GENE_CODE_STR[antigen.upper()]


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


def get_filtered_antigens(hla_types: List[HLAType], antigen: HLATypes) -> List[str]:
    """
    Gets list of antigens codes of particular HLA type.
    :param hla_types:
    :param antigen:
    :return: List of codes.
    """
    return list(
        map(lambda x: x.code,
            filter(lambda x: False if x.code is None else x.code.upper().startswith(antigen.upper()), hla_types)))


def get_other_antigens(hla_types: List[HLAType]) -> List[str]:
    """
    Gets other HLA types except types defined in HLAType.
    :param hla_types:
    :return: List of codes.
    """
    return list(
        map(lambda x: x.code,
            filter(lambda x: not _start_with(x.code, [hla.value for hla in HLATypes]), hla_types)))


def get_filtered_antibodies(antibodies: HLAAntibodies, antigen: HLATypes) -> List[str]:
    """
    Gets list of antibodies codes of particular HLA type.
    :param antibodies:
    :param antigen:
    :return: List of codes.
    """
    return [code for code in
            list(filter(lambda x: x.upper().startswith(antigen.upper()), antibodies.hla_codes_over_cutoff))]


def get_other_antibodies(antibodies: HLAAntibodies) -> List[str]:
    """
    Gets other HLA types except types defined in HLAType.
    :param antibodies:
    :return: List of codes.
    """
    return list(filter(lambda x: not _start_with(x, [hla.value for hla in HLATypes]), antibodies.hla_codes_over_cutoff))


def _start_with(value: str, values: List[str]) -> bool:
    for val in values:
        if value.upper().startswith(val):
            return True
    return False
