from typing import List

from txmatching.configuration.configuration import Configuration
from txmatching.filters.filter_base import FilterBase
from txmatching.solvers.matching.matching import Matching


class FilterDefault(FilterBase):
    @classmethod
    def from_config(cls, configuration: Configuration) -> 'FilterBase':
        return FilterDefault(
            required_patient_db_ids=configuration.required_patient_db_ids
        )

    def __init__(self, required_patient_db_ids: List[int]):
        self._required_patients = required_patient_db_ids

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        for patient_db_id in self._required_patients:
            if not any([transplant_round.contains_patient_db_id(patient_db_id) for transplant_round in
                        sequences + cycles]):
                return False

        return True
