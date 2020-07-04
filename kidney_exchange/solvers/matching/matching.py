from typing import List, Tuple, Set

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.transplant_cycle import TransplantCycle
from kidney_exchange.solvers.matching.transplant_round import TransplantRound
from kidney_exchange.solvers.matching.transplant_sequence import TransplantSequence


class Matching:
    """
    Set of disjoint TransplantRound's
    """

    def __init__(self, donor_recipient_list: List[Tuple[Donor, Recipient]] = None):
        # TODO list of TransplantRounds?
        self._donor_recipient_list = donor_recipient_list

    @property
    def donor_recipient_list(self):
        return self._donor_recipient_list

    def get_cycles(self) -> Set[TransplantCycle]:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement

    def get_sequences(self) -> Set[TransplantSequence]:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement

    def get_rounds(self) -> Set[TransplantRound]:
        cycles = self.get_cycles()
        sequences = self.get_sequences()
        return set.union(cycles, sequences)
