from typing import FrozenSet, Iterable, List, Set, Tuple
from unittest import TestCase

from txmatching.utils.hla_system.hla_preparation_utils import create_antibodies
from txmatching.patients.hla_model import HLATyping
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching import Matching
from txmatching.solvers.matching.transplant_round import TransplantRound
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country


def _create_recipient(recipient_id: int, donor: Donor) -> Recipient:
    return Recipient(recipient_id,
                     f'R-{recipient_id}',
                     related_donors_db_ids=[donor.db_id],
                     etag=1,
                     parameters=PatientParameters(
                         country_code=Country.CZE, blood_group=BloodGroup.A,
                         hla_typing=HLATyping(hla_per_groups=[], hla_types_raw_list=[])
                     ),
                     acceptable_blood_groups=list(),
                     hla_antibodies=create_antibodies([]),
                     parsing_issues=[]
                     )


def _inner_elements_to_frozenset(iterable: Iterable) -> Set[FrozenSet]:
    return {frozenset(item) for item in iterable}


class TestMatching(TestCase):
    def setUp(self) -> None:
        self._donors = [
            Donor(donor_index, f'D-{donor_index}', etag=1,
                  parameters=PatientParameters(blood_group=BloodGroup.A, country_code=Country.CZE,
                                               hla_typing=HLATyping(hla_per_groups=[], hla_types_raw_list=[])),
                                               parsing_issues=[])
            for donor_index in range(10)]
        self._recipients = [_create_recipient(10 + donor_index, donor)
                            for donor_index, donor in enumerate(self._donors)]

        # transplant_indices - (donor_index, recipient_index)
        # expected_cycles - each cycle represented by a set of (donor_index, recipient_index)
        # expected_sequences - each sequence represented by a set of (donor_index, recipient_index)
        self._transplant_indices_1 = [(4, 1), (2, 3), (1, 2), (5, 6), (3, 4), (6, 7)]
        self._expected_cycles_1 = [{(1, 2), (2, 3), (3, 4), (4, 1)}]
        self._expected_sequences_1 = [{(5, 6), (6, 7)}]

        self._transplant_indices_2 = [(6, 7), (2, 3), (1, 2), (3, 4), (4, 5), (5, 6)]
        self._expected_cycles_2 = []
        self._expected_sequences_2 = [{(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)}]

        self._transplant_indices_3 = [(1, 4), (2, 3), (4, 1), (3, 2), (8, 9)]
        self._expected_cycles_3 = [{(4, 1), (1, 4)}, {(2, 3), (3, 2)}]
        self._expected_sequences_3 = [{(8, 9)}]

        self._transplant_indices_4 = [(2, 3), (6, 4), (3, 1), (4, 5), (5, 6), (1, 2), (7, 8), (8, 7)]
        self._expected_cycles_4 = [{(7, 8), (8, 7)}, {(1, 2), (2, 3), (3, 1)}, {(4, 5), (5, 6), (6, 4)}]
        self._expected_sequences_4 = []

        self._transplant_indices_5 = [(4, 1), (5, 2), (6, 3), (3, 4), (8, 9), (2, 7)]
        self._expected_cycles_5 = []
        self._expected_sequences_5 = [{(5, 2), (2, 7)}, {(6, 3), (3, 4), (4, 1)}, {(8, 9)}]

        self._test_cases = [(self._transplant_indices_1, self._expected_cycles_1, self._expected_sequences_1),
                            (self._transplant_indices_2, self._expected_cycles_2, self._expected_sequences_2),
                            (self._transplant_indices_3, self._expected_cycles_3, self._expected_sequences_3),
                            (self._transplant_indices_4, self._expected_cycles_4, self._expected_sequences_4),
                            (self._transplant_indices_5, self._expected_cycles_5, self._expected_sequences_5)]

        self._test_cases = [(transplant_indices,
                             _inner_elements_to_frozenset(expected_cycles),
                             _inner_elements_to_frozenset(expected_sequences))
                            for transplant_indices, expected_cycles, expected_sequences in self._test_cases]

    def _make_matching_from_donor_recipient_indices(self, donor_recipient_indices: List[Tuple[int, int]]) \
            -> Matching:
        donor_recipient_pairs = frozenset(
            DonorRecipientPair(self._donors[donor_index], self._recipients[recipient_index])
            for donor_index, recipient_index in donor_recipient_indices)
        return Matching(donor_recipient_pairs)

    def _transplant_round_to_indices(self, transplant_round: TransplantRound) -> frozenset:
        donor_recipient_indices = {(self._donors.index(donor_recipient.donor),
                                    self._recipients.index(donor_recipient.recipient))
                                   for donor_recipient in transplant_round.donor_recipient_pairs}
        return frozenset(donor_recipient_indices)

    def test_get_cycles(self):
        for transplant_indices, expected_cycles, _ in self._test_cases:
            matching = self._make_matching_from_donor_recipient_indices(transplant_indices)
            cycles = matching.get_cycles()
            index_cycles = {self._transplant_round_to_indices(cycle) for cycle in cycles}
            self.assertEqual(index_cycles, expected_cycles)

    def test_get_sequences(self):
        for transplant_indices, _, expected_sequences in self._test_cases:
            matching = self._make_matching_from_donor_recipient_indices(transplant_indices)
            sequences = matching.get_sequences()
            index_sequences = {self._transplant_round_to_indices(sequence) for sequence in sequences}
            self.assertEqual(index_sequences, expected_sequences)
