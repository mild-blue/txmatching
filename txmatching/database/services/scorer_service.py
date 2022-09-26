import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from dacite import from_dict

from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.scorers.compatibility_graph import CompatibilityGraph


@dataclass
class CompatibilityGraphDto:
    compatibility_graph_dto: List[List[float]]


def compatibility_graph_to_dict(compatibility_graph: CompatibilityGraph) -> Dict[str, CompatibilityGraph]:
    return dataclasses.asdict(CompatibilityGraphDto(compatibility_graph))


def compatibility_graph_from_dict(compatibility_graph_dict: Dict[str, CompatibilityGraph]) -> CompatibilityGraph:
    compatibility_graph_dto = from_dict(data_class=CompatibilityGraphDto, data=compatibility_graph_dict)
    return compatibility_graph_dto.compatibility_graph_dto


def matchings_model_from_dict(calculated_matchings_dict: Dict[str, any]) -> MatchingsModel:
    return from_dict(data_class=MatchingsModel,
                     data=calculated_matchings_dict)
