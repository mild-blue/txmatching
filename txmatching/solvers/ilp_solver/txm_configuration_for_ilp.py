from dataclasses import dataclass
from typing import Iterable, Tuple

import networkx as nx


@dataclass
class DataAndConfigurationForILPSolver:
    num_nodes: int
    non_directed_donors: Iterable[int]
    edges: Iterable[Tuple[int, int, int]]
    max_cycle_length: int  # in number of edges.
    max_sequence_length: int  # in number of edges.

    def __post_init__(self):
        self.graph = nx.DiGraph()

        self.graph.add_nodes_from([
            (node, {'ndd': node in self.non_directed_donors})
            for node in range(0, self.num_nodes)
        ])

        self.graph.add_edges_from([
            (from_node, to_node, {'weight': weight})
            for (from_node, to_node, weight) in self.edges
        ])

        self.dp_pairs = set(self.graph.nodes()) - set(self.non_directed_donors)
