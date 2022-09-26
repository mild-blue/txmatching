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


def compatibility_graph_to_dict(compatibility_graph: CompatibilityGraph) -> Dict[str, List[List[float]]]:
    list_of_lists = [[int(pair[0]), int(pair[1]), score] for pair, score in compatibility_graph.items()]
    return dataclasses.asdict(CompatibilityGraphDto(list_of_lists))


def compatibility_graph_from_dict(compatibility_graph_dict: Dict[str, List[List[float]]]) -> CompatibilityGraph:
    compatibility_graph_dto = from_dict(data_class=CompatibilityGraphDto, data=compatibility_graph_dict)
    compatibility_graph = {(int(single_list[0]), int(single_list[1])): single_list[2] for single_list in
                           compatibility_graph_dto.compatibility_graph_dto}
    return compatibility_graph


def matchings_model_from_dict(calculated_matchings_dict: Dict[str, any]) -> MatchingsModel:
    return from_dict(data_class=MatchingsModel,
                     data=calculated_matchings_dict)
