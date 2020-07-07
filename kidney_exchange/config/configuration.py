import json
from json import JSONEncoder
from typing import List


class ConfigEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


_config_encoder = ConfigEncoder()


class Configuration:
    def __init__(self, scorer_constructor_name: str = "HLAAdditiveScorer",
                 solver_constructor_name: str = "AllSolutionsSolver",
                 enforce_same_blood_group: bool = True,
                 minimum_compatibility_index: float = 0.0,
                 require_new_donor_having_better_match_in_compatibility_index: bool = True,
                 require_new_donor_having_better_match_in_compatibility_index_or_blood_group: bool = True,
                 use_binary_scoring: bool = False,
                 max_cycle_length: int = 5,
                 max_sequence_length: int = 5,
                 max_number_of_distinct_countries_in_round: int = 2,
                 required_patient_ids: List[str] = None):
        self._solver_constructor_name = solver_constructor_name
        self._scorer_constructor_name = scorer_constructor_name
        self._enforce_same_blood_group = enforce_same_blood_group
        self._minimum_compatibility_index = minimum_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index = require_new_donor_having_better_match_in_compatibility_index
        self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group = require_new_donor_having_better_match_in_compatibility_index_or_blood_group
        self._use_binary_scoring = use_binary_scoring
        self._max_cycle_length = max_cycle_length
        self._max_sequence_length = max_sequence_length
        self._max_number_of_distinct_countries_in_round = max_number_of_distinct_countries_in_round
        self._required_patient_ids = required_patient_ids or []

    @property
    def solver_constructor_name(self):
        return self._solver_constructor_name

    @property
    def scorer_constructor_name(self):
        return self._scorer_constructor_name

    @property
    def enforce_same_blood_group(self):
        return self._enforce_same_blood_group

    @property
    def minimum_compatibility_index(self):
        return self._minimum_compatibility_index

    @property
    def require_new_donor_having_better_match_in_compatibility_index(self):
        return self._require_new_donor_having_better_match_in_compatibility_index

    @property
    def require_new_donor_having_better_match_in_compatibility_index_or_blood_group(self):
        return self._require_new_donor_having_better_match_in_compatibility_index_or_blood_group

    @property
    def use_binary_scoring(self):
        return self._use_binary_scoring

    @property
    def max_cycle_length(self):
        return self._max_cycle_length

    @property
    def max_sequence_length(self):
        return self._max_sequence_length

    @property
    def max_number_of_distinct_countries_in_round(self):
        return self._max_number_of_distinct_countries_in_round

    @property
    def required_patient_ids(self):
        return self._required_patient_ids

    def serialize(self) -> str:
        serialized_config = _config_encoder.encode(self)
        return serialized_config

    @classmethod
    def deserialize(cls, config_json: str) -> "Configuration":
        config_kwargs = json.loads(config_json)
        # TODO: This is dirty trick to remove the underscore from the private field names, refactor
        config_kwargs = {key[1:]: value for key, value in config_kwargs.items()}
        return Configuration(**config_kwargs)


if __name__ == "__main__":
    config = Configuration()
    serialized_configuration = config.serialize()
    print(serialized_configuration)
    deserialized_config = Configuration.deserialize(serialized_configuration)
    print(deserialized_config)
