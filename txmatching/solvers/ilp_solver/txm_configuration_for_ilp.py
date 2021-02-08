# pylint: skip-file
# TODO: improve the code https://github.com/mild-blue/txmatching/issues/430

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import networkx as nx


@dataclass
class TXMConfigurationForILPSolver:
    num_nodes: int
    non_directed_donors: Iterable[int]
    edges: Iterable[Tuple[int, int, int]]
    max_cycle_length: int  # in number of edges.
    max_sequence_length: int  # in number of edges.
    node_labels: Dict[int, str] = None

    def __post_init__(self):
        self.graph = nx.DiGraph()

        if self.node_labels is None:
            self.node_labels = {node: str(node) for node in range(0, self.num_nodes)}

        self.graph.add_nodes_from([
            (node, {'ndd': node in self.non_directed_donors, 'label': self.node_labels[node]})
            for node in range(0, self.num_nodes)
        ])

        self.graph.add_edges_from([
            (from_node, to_node, {'weight': weight})
            for (from_node, to_node, weight) in self.edges
        ])

        self.dp_pairs = set(self.graph.nodes()) - set(self.non_directed_donors)


class InstanceTransform:

    @staticmethod
    def unit_weights(ins: TXMConfigurationForILPSolver) -> TXMConfigurationForILPSolver:
        return TXMConfigurationForILPSolver(
            num_nodes=ins.graph.number_of_nodes(),
            non_directed_donors=ins.non_directed_donors,
            edges=[(from_node, to_node, 1) for from_node, to_node in ins.graph.edges],
            max_cycle_length=ins.max_cycle_length,
            max_sequence_length=ins.max_sequence_length,
            node_labels=nx.get_node_attributes(ins.graph, 'label')
        )


def create_example_1():
    '''Taken from [1], Fig. S3. The weight of all edges equals 1.'''
    return TXMConfigurationForILPSolver(
        num_nodes=8,
        non_directed_donors=[0],
        edges=[
            (0, 1, 1),
            (1, 2, 1),
            (2, 3, 1),
            (3, 7, 1),
            (2, 6, 1),
            (6, 5, 1),
            (5, 6, 1),
            (5, 4, 1),
        ],
        max_cycle_length=3,
        max_sequence_length=3
    )


def create_example_2():
    '''Taken from [1], Fig. S4. The weight of all edges equals 1.'''
    return TXMConfigurationForILPSolver(
        num_nodes=7,
        non_directed_donors=[0],
        edges=[
            (0, 1, 1),
            (0, 2, 1),
            (2, 1, 1),
            (2, 3, 1),
            (2, 4, 1),
            (3, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 3, 1),
        ],
        max_cycle_length=4,
        max_sequence_length=4
    )


def create_example_3():
    '''Taken from [1], Fig. S4. The weight of all edges equals 1.'''
    return TXMConfigurationForILPSolver(
        num_nodes=7,
        non_directed_donors=[0],
        edges=[
            (0, 1, 1),
            (0, 2, 1),
            (2, 1, 1),
            (2, 3, 1),
            (2, 4, 1),
            (3, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 3, 1),
        ],
        max_cycle_length=3,
        max_sequence_length=3
    )
