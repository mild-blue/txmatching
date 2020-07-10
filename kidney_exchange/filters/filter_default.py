from typing import List
import numpy as np
from kidney_exchange.config.configuration import Configuration
from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.patients.patient import Patient
from kidney_exchange.solvers.matching.matching import Matching


class FilterDefault(FilterBase):
    @classmethod
    def from_config(cls, configuration: Configuration) -> "FilterBase":
        return FilterDefault(max_cycle_length=configuration.max_cycle_length,
                             max_sequence_length=configuration.max_sequence_length,
                             max_number_of_distinct_countries_in_round=configuration.max_number_of_distinct_countries_in_round,
                             required_patients=[Patient(patient_id) for patient_id in
                                                configuration.required_patient_ids])

    def __init__(self, max_cycle_length: int = None,
                 max_sequence_length: int = None,
                 max_number_of_distinct_countries_in_round: int = None,
                 required_patients: List[Patient] = None):
        self._max_cycle_length = max_cycle_length
        self._max_sequence_length = max_sequence_length
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round
        self._required_patients = required_patients

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        if max([cycle.length for cycle in cycles], default=-np.inf) > self._max_cycle_length:
            return False

        if max([sequence.length for sequence in sequences], default=-np.inf) > self._max_sequence_length:
            return False

        if max([transplant_round.country_count for transplant_round in
                set.union(sequences, cycles)]) > self._max_number_of_distinct_countries_in_round:
            return False

        for patient in self._required_patients:
            if not any([transplant_round.contains_patient(patient) for transplant_round in set.union(sequences, cycles)]):
                return False

        return True
