import unittest
from typing import List

from tests.test_utilities.create_dataclasses import (get_test_antibodies,
                                                     get_test_donors,
                                                     get_test_raw_codes,
                                                     get_test_recipients)
from txmatching.patients.patient import Patient
from txmatching.scorers.matching import get_count_of_transplants
from txmatching.scorers.split_hla_additive_scorer import \
    SplitHLAAdditiveScorerCIConfiguration
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.matching.transplant_cycle import TransplantCycle
from txmatching.solvers.matching.transplant_sequence import TransplantSequence
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.hla_system.compatibility_index import \
    get_detailed_compatibility_index

RAW_CODES = get_test_raw_codes()

DONORS = get_test_donors()

RECIPIENTS = get_test_recipients()

TEST_ANTIBODIES = get_test_antibodies()


def calculate_compatibility_index_for_group(donor: Patient, recipient: Patient, hla_group: HLAGroup) -> float:
    """
    Calculates antigen score of donor and recipient of particular HLA type.
    :param donor:
    :param recipient:
    :param hla_group:
    :return: Score value.
    """

    scores = get_detailed_compatibility_index(donor.parameters.hla_typing,
                                              recipient.parameters.hla_typing,
                                              ci_configuration=SplitHLAAdditiveScorerCIConfiguration())
    return next(group_ci_detailed.group_compatibility_index for group_ci_detailed in scores if
                group_ci_detailed.hla_group == hla_group)


class TestMatching(unittest.TestCase):

    def _get_matching_hla_typing_display_code(self, donor: Patient, recipient: Patient) -> List[str]:
        """
        Gets matching HLA typings of donor and recipient.
        :param donor:
        :param recipient:
        :return: List of same HLA typings of donor and recipient.
        """
        scores = get_detailed_compatibility_index(donor.parameters.hla_typing,
                                                  recipient.parameters.hla_typing)
        return list({match.hla_type.code.display_code for ci_detail_group in scores
                     for match in ci_detail_group.recipient_matches
                     if match.match_type != MatchTypes.NONE})

    def test_get_matching_hla_typing(self):
        result = self._get_matching_hla_typing_display_code(DONORS[0], RECIPIENTS[0])
        result.sort()
        self.assertListEqual([RAW_CODES[1]], result)

        result = self._get_matching_hla_typing_display_code(DONORS[0], RECIPIENTS[1])
        result.sort()
        self.assertListEqual([], result)

        result = self._get_matching_hla_typing_display_code(DONORS[1], RECIPIENTS[0])
        result.sort()
        self.assertListEqual([RAW_CODES[1], RAW_CODES[2]], result)

        result = self._get_matching_hla_typing_display_code(DONORS[1], RECIPIENTS[1])
        result.sort()
        self.assertListEqual([], result)

    def test_calculate_antigen_score(self):
        # A32
        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroup.A)
        self.assertEquals(1, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroup.B)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroup.DRB1)
        self.assertEquals(0, result)

        # No match
        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroup.A)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroup.B)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroup.DRB1)
        self.assertEquals(0, result)

        # A32, B7
        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroup.A)
        self.assertEquals(2, result)

        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroup.B)
        self.assertEquals(6, result)

        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroup.DRB1)
        self.assertEquals(0, result)

    def test_get_count_of_transplants(self):
        matching = MatchingWithScore(
            matching_pairs=frozenset(),
            score=0,
            order_id=0
        )

        result = get_count_of_transplants(matching)
        self.assertEquals(0, result)

        matching = MatchingWithScore(
            matching_pairs=frozenset(),
            score=0,
            order_id=0
        )

        matching._cycles = [
            TransplantCycle(donor_recipient_pairs=[DonorRecipientPair(DONORS[0], RECIPIENTS[0])]),
            TransplantCycle(donor_recipient_pairs=[]),
            TransplantCycle(donor_recipient_pairs=[
                DonorRecipientPair(DONORS[0], RECIPIENTS[0]),
                DonorRecipientPair(DONORS[1], RECIPIENTS[1]),
            ]),
        ]

        matching._sequences = [
            TransplantSequence(donor_recipient_pairs=[
                DonorRecipientPair(DONORS[0], RECIPIENTS[0]),
            ])
        ]

        result = get_count_of_transplants(matching)
        self.assertEquals(4, result)
