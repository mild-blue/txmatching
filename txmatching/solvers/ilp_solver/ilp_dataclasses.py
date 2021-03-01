from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Tuple

import mip

from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver


class MaxSequenceLimitMethod(IntEnum):
    LazyForbidAllMaximalSequences = 0
    '''Lazy constraints. Forbid all maximal sequences that are larger than the limit.'''

    LazyForbidSmallestMaximalSequence = 1
    '''Lazy constraints. Forbid smallest maximal sequences that is larger than the limit.'''
    # TODO understand the purpose of this option
    # LazyForbidAllSubsequences = 2
    # '''Lazy constraints. Forbid all subsequences that are larger than the limit.'''


class ObjectiveType(IntEnum):
    MaxTransplants = 0
    '''Maximize the number of transplants.'''

    MaxWeights = 1
    '''Maximize the total transplants weights.'''

    MaxTransplantsMaxWeights = 2
    '''Maximize the number of transplants and then maximize their total weight.'''


@dataclass
class InternalILPSolverParameters:
    objective_type: ObjectiveType = ObjectiveType.MaxTransplantsMaxWeights
    max_sequence_limit_method: MaxSequenceLimitMethod = MaxSequenceLimitMethod.LazyForbidAllMaximalSequences


@dataclass(init=False)
class VariableMapping:
    edge_to_var: Dict[Tuple[int, int], mip.Var]
    node_to_in_var: Dict[int, mip.Var]
    node_to_out_var: Dict[int, mip.Var]

    def __init__(self, ilp_model: mip.Model, data_and_configuration: DataAndConfigurationForILPSolver):
        # Mapping from edge e to variable y_e
        self.edge_to_var = dict()
        for (from_node, to_node) in data_and_configuration.graph.edges():
            self.edge_to_var[from_node, to_node] = ilp_model.add_var(var_type=mip.BINARY,
                                                                     name=f'y[{from_node},{to_node}]')

        # Mapping from node v to variable f^i_v
        self.node_to_in_var = dict()
        for node in data_and_configuration.graph.nodes():
            self.node_to_in_var[node] = ilp_model.add_var(lb=0, var_type=mip.INTEGER, name=f'fi[{node}]')

        # Mapping from node v to variable f^o_v
        self.node_to_out_var = dict()
        for node in data_and_configuration.graph.nodes():
            self.node_to_out_var[node] = ilp_model.add_var(lb=0, var_type=mip.INTEGER, name=f'fo[{node}]')
