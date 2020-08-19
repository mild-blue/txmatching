from typing import List

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.solvers.matching.matching import Matching


class FilterDefault(FilterBase):
    @classmethod
    def from_config(cls, configuration: Configuration) -> 'FilterBase':
        return FilterDefault(max_cycle_length=configuration.max_cycle_length,
                             max_sequence_length=configuration.max_sequence_length,
                             max_number_of_distinct_countries_in_round=
                             configuration.max_number_of_distinct_countries_in_round,
                             required_patient_db_ids=configuration.required_patient_db_ids
                             )

    def __init__(self, max_cycle_length: int = None,
                 max_sequence_length: int = None,
                 max_number_of_distinct_countries_in_round: int = None,
                 required_patient_db_ids: List[int] = None):
        self._max_cycle_length = max_cycle_length
        self._max_sequence_length = max_sequence_length
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round
        self._required_patients = required_patient_db_ids

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        if self._max_cycle_length is not None \
                and max([cycle.length for cycle in cycles], default=0) > self._max_cycle_length:
            return False

        if self._max_sequence_length is not None and \
                max([sequence.length for sequence in sequences], default=0) > self._max_sequence_length:
            return False

        # TODO update to get even non-maximal matchings, i.e. with 1 country only
        #  https://trello.com/c/HL4xunKV/132-solver-does-not-return-trivial-matchings
        if max([transplant_round.country_count for transplant_round in
                sequences + cycles]) > self._max_number_of_distinct_countries_in_round:
            return False

        for patient_db_id in self._required_patients:
            if not any([transplant_round.contains_patient_db_id(patient_db_id) for transplant_round in
                        sequences + cycles]):
                return False

        return True
