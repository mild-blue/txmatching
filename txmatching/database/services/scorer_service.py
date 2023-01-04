from dataclasses import dataclass
from typing import Dict, List

from dacite import from_dict

from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.scorers.scorer_constants import HLA_SCORE


@dataclass
class CompatibilityGraphDto:
    compatibility_graph_dto: List[List[int]]


def compatibility_graph_to_dict(compatibility_graph: CompatibilityGraph) -> Dict[str, List[List[int]]]:
    return {"compatibility_graph_dto": [[int(pair[0]), int(pair[1]), weighths[HLA_SCORE]]
                                        for pair, weighths in compatibility_graph.items()]}


def compatibility_graph_from_dict(compatibility_graph_dict: Dict[str, List[List[int]]]) -> CompatibilityGraph:
    return {(pair[0], pair[1]): {HLA_SCORE: pair[2]} for pair in
            compatibility_graph_dict["compatibility_graph_dto"]}


def matchings_model_from_dict(calculated_matchings_dict: Dict[str, any]) -> MatchingsModel:
    return from_dict(data_class=MatchingsModel,
                     data=calculated_matchings_dict)
