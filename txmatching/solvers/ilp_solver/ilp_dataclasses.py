from dataclasses import dataclass
from enum import IntEnum


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
