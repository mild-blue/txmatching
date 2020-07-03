from typing import List, Tuple, Set, Sequence

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.cycle import Cycle
from kidney_exchange.solvers.matching.round import Round


class Matching:
    """
    Set of disjoint Round's
    """

    def __init__(self, donor_recipient_list: List[Tuple[Donor, Recipient]] = None):
        self._donor_recipient_list = donor_recipient_list

    @property
    def donor_recipient_list(self):
        return self._donor_recipient_list

    def get_cycles(self) -> Set[Cycle]:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement

    def get_sequences(self) -> Set[Sequence]:
        raise NotImplementedError("TODO: Implement")  # TODO: Implement

    def get_rounds(self) -> Set[Round]:
        cycles = self.get_cycles()
        sequences = self.get_sequences()
        return set.union(cycles, sequences)
