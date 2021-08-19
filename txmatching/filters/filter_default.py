from dataclasses import dataclass

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.filters.filter_base import FilterBase
from txmatching.solvers.matching.matching import Matching


@dataclass
class FilterDefault(FilterBase):
    configuration: ConfigParameters

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'FilterBase':
        return FilterDefault(config_parameters)

    def keep(self, matching: Matching) -> bool:
        sequences = matching.get_sequences()
        cycles = matching.get_cycles()

        for patient_db_id in self.configuration.required_patient_db_ids:
            if not any([transplant_round.contains_patient_db_id(patient_db_id) for transplant_round in
                        sequences + cycles]):
                return False
        if matching.max_debt_from_matching > self.configuration.max_debt_for_country:
            return False

        if matching.max_blood_group_zero_debt_from_matching \
                > self.configuration.max_debt_for_country_for_blood_group_zero:
            return False
        return True
