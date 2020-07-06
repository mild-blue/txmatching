import json
from json import JSONEncoder
from typing import List

from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.filters.filter_default import FilterDefault
from kidney_exchange.patients.patient import Patient
from kidney_exchange.scorers.hla_additive_scorer import HLAAdditiveScorer
from kidney_exchange.scorers.scorer_base import ScorerBase
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.solvers.solver_base import SolverBase


class ConfigEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


_config_encoder = ConfigEncoder()


class Configuration:
    _supported_scorers = [cls.__name__ for cls in [HLAAdditiveScorer]]
    _supported_solvers = [cls.__name__ for cls in [AllSolutionsSolver]]

    def __init__(self, scorer_constructor_name: str = HLAAdditiveScorer.__name__,
                 solver_constructor_name: str = AllSolutionsSolver.__name__,
                 enforce_same_blood_group: bool = True,
                 minimum_compatibility_index: float = 0.0,
                 require_new_donor_having_better_match_in_compatibility_index: bool = True,
                 require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True,
                 use_binary_scoring: bool = False,
                 max_cycle_lenght: int = 5,
                 max_sequence_lenght: int = 5,
                 max_number_of_distinct_countries_in_round: int = 2,
                 required_patient_ids: List[str] = None):
        self._solver_constructor_name = solver_constructor_name
        self._scorer_constructor_name = scorer_constructor_name
        self._enforce_same_blood_group = enforce_same_blood_group
        self._minimum_compatibility_index = minimum_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index = require_new_donor_having_better_match_in_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group = require_new_donor_having_better_match_in_compatibility_index_or_blood_group
        self._use_binary_scoring = use_binary_scoring
        self._max_cycle_lenght = max_cycle_lenght
        self._max_sequence_lenght = max_sequence_lenght
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round
        self._required_patient_ids = required_patient_ids or []

    def create_scorer(self) -> ScorerBase:
        if self._scorer_constructor_name not in Configuration._supported_scorers:
            raise NotImplementedError(f"Scorer {self._scorer_constructor_name} not supported yet")

        if self._scorer_constructor_name == HLAAdditiveScorer.__name__:
            scorer = HLAAdditiveScorer(enforce_same_blood_group=self._enforce_same_blood_group,
                                       minimum_compatibility_index=self._minimum_compatibility_index,
                                       require_new_donor_having_better_match_in_compatibility_index=self._require_new_donor_having_better_match_in_compatibility_index,
                                       require_new_donor_having_better_match_in_compatibility_index_or_blood_group=self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group,
                                       use_binary_scoring=self._use_binary_scoring)

        return scorer

    def create_solver(self) -> SolverBase:
        if self._solver_constructor_name not in Configuration._supported_scorers:
            raise NotImplementedError(f"Solver {self._solver_constructor_name} not supported yet")

        if self._solver_constructor_name == AllSolutionsSolver.__name__:
            solver = AllSolutionsSolver()

        return solver

    def create_filter(self) -> FilterBase:
        filter = FilterDefault(max_cycle_lenght=self._max_cycle_lenght,
                               max_sequence_lenght=self._max_sequence_lenght,
                               max_number_of_distinct_countries_in_round=self._max_number_of_distinct_countries_in_round,
                               required_patients=[Patient(patient_id) for patient_id in self._required_patient_ids])
        return filter

    def serialize(self) -> str:
        serialized_config = _config_encoder.encode(self)
        return serialized_config

    @classmethod
    def deserialize(self, config_json: str) -> "Configuration":
        config_kwargs = json.loads(config_json)
        # TODO: This is dirty trick to remove the underscore from the private field names, refactor
        config_kwargs = {key[1:]: value for key, value in config_kwargs.items()}
        return Configuration(**config_kwargs)


if __name__ == "__main__":
    config = Configuration()
    serialized_config = config.serialize()
    print(serialized_config)
    deserialized_config = Configuration.deserialize(serialized_config)
    print(deserialized_config)
