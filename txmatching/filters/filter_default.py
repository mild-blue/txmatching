from dataclasses import dataclass

from txmatching.configuration.configuration import Configuration
from txmatching.filters.filter_base import FilterBase
from txmatching.solvers.matching.matching import Matching


@dataclass
class FilterDefault(FilterBase):
    configuration: Configuration

    @classmethod
    def from_config(cls, configuration: Configuration) -> 'FilterBase':
        return FilterDefault(configuration)

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        for patient_db_id in self.configuration.required_patient_db_ids:
            if not any([transplant_round.contains_patient_db_id(patient_db_id) for transplant_round in
                        sequences + cycles]):
                return False
        if matching.max_debt_from_matching() > self.configuration.max_debt_for_country:
            return False

        return True
