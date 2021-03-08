from dataclasses import dataclass
from typing import FrozenSet, List, Set

import numpy as np

from txmatching.data_transfer_objects.matchings.matching_dto import CountryDTO
from txmatching.patients.patient import DonorType
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.transplant_cycle import TransplantCycle
from txmatching.solvers.matching.transplant_round import TransplantRound
from txmatching.solvers.matching.transplant_sequence import TransplantSequence
from txmatching.utils.country_enum import Country


@dataclass
class Matching:
    """
    Set of disjoint TransplantRound's
    """
    matching_pairs: FrozenSet[DonorRecipientPair]

    def __post_init__(self):
        matching_pairs = list(self.matching_pairs)
        recipients = [pair.recipient for pair in matching_pairs]
        donor_ids = [pair.donor.db_id for pair in matching_pairs]

        # Construct graph with vertices indexed by transplants
        # Edges tell us which transplant will come next
        vertices = list(range(len(matching_pairs)))
        edges = {recipient_index: donor_ids.index(recipient.related_donor_db_id) for recipient_index, recipient
                 in enumerate(recipients) if recipient.related_donor_db_id in donor_ids}
        reverse_edges = {dest_vertex: source_vertex for source_vertex, dest_vertex in edges.items()}

        unprocessed_vertices = set(vertices)

        vertex_cycles = set()
        vertex_sequences = set()

        while len(unprocessed_vertices) > 0:
            start_vertex = unprocessed_vertices.pop()
            next_vertex = edges.get(start_vertex)
            vertex_round = [start_vertex]
            while next_vertex is not None and next_vertex != start_vertex:
                vertex_round.append(next_vertex)
                unprocessed_vertices.remove(next_vertex)
                next_vertex = edges.get(next_vertex)

            if next_vertex == start_vertex:
                vertex_cycles.add(tuple(vertex_round))
            elif next_vertex is None:
                previous_vertex = reverse_edges.get(start_vertex)
                while previous_vertex is not None:
                    vertex_round.insert(0, previous_vertex)
                    unprocessed_vertices.remove(previous_vertex)
                    previous_vertex = reverse_edges.get(previous_vertex)
                vertex_sequences.add(tuple(vertex_round))
            else:
                raise AssertionError('Next vertex is not None nor equal to start vertex')

        self._cycles = list(TransplantCycle([matching_pairs[i] for i in cycle])
                            for cycle in vertex_cycles)
        self._sequences = list(TransplantSequence([matching_pairs[i] for i in seq])
                               for seq in vertex_sequences)

    def get_donor_recipient_pairs(self):
        return self.matching_pairs

    def get_non_directed_count(self):
        return len([donor for donor, _ in self.matching_pairs if donor.donor_type == DonorType.NON_DIRECTED])

    def get_bridging_donor_count(self):
        return len(
            [donor for donor, _ in self.matching_pairs if donor.donor_type == DonorType.BRIDGING_DONOR])

    def get_donors_for_country_count(self, country_code: str):
        return len([pair.donor.parameters.country_code for pair in self.matching_pairs if
                    pair.donor.parameters.country_code == country_code])

    def get_recipients_for_country_count(self, country_code: str):
        return len([pair.recipient.parameters.country_code for pair in self.matching_pairs if
                    pair.recipient.parameters.country_code == country_code])

    def get_country_codes_counts(self) -> List[CountryDTO]:

        return [CountryDTO(country,
                           self.get_donors_for_country_count(country),
                           self.get_recipients_for_country_count(country)) for country in self._countries]

    def get_cycles(self) -> List[TransplantCycle]:
        return self._cycles

    def get_sequences(self) -> List[TransplantSequence]:
        return self._sequences

    def get_rounds(self) -> List[TransplantRound]:
        cycles = self.get_cycles()
        sequences = self.get_sequences()
        return cycles + sequences

    @property
    def _countries(self) -> Set[Country]:
        return {patient.parameters.country_code for donor_recipient in self.matching_pairs for patient in
                [donor_recipient.donor, donor_recipient.recipient]}

    @property
    def max_debt_from_matching(self) -> int:
        return max([np.abs([self.get_donors_for_country_count(country) -
                            self.get_recipients_for_country_count(country)])
                    for country in self._countries])
