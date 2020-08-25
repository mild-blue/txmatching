from typing import List, Tuple, Set, Iterable, FrozenSet
from unittest import TestCase

from txmatching.patients.donor import Donor
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.recipient import Recipient
from txmatching.solvers.matching.matching import Matching
from txmatching.solvers.matching.transplant_round import TransplantRound


def _create_recipient(idd: int, donor: Donor) -> Recipient:
    return Recipient(idd, f"R-{idd}", related_donor=donor, parameters=PatientParameters())


def _inner_elements_to_frozenset(iterable: Iterable) -> Set[FrozenSet]:
    return {frozenset(item) for item in iterable}


class TestMatching(TestCase):
    def setUp(self) -> None:
        self._donors = [Donor(donor_index, f"D-{donor_index}", parameters=PatientParameters())
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
        donor_recipient_list = [(self._donors[donor_index], self._recipients[recipient_index])
                                for donor_index, recipient_index in donor_recipient_indices]
        return Matching(donor_recipient_list)

    def _transplant_round_to_indices(self, transplant_round: TransplantRound) -> frozenset:
        donor_recipient_indices = {(self._donors.index(donor), self._recipients.index(recipient))
                                   for donor, recipient in transplant_round.donor_recipient_list}
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
