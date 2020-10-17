from typing import Dict

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.all_solutions_solver import \
    AllSolutionsSolver
from txmatching.solvers.solver_base import SolverBase

_supported_solvers = [AllSolutionsSolver]


def solver_from_configuration(configuration: Configuration,
                              donors_dict: Dict[DonorDbId, Donor],
                              recipients_dict: Dict[RecipientDbId, Recipient],
                              scorer: AdditiveScorer) -> SolverBase:
    solver_dict = {supported_object.__name__: supported_object for supported_object in _supported_solvers}
    solver = solver_dict.get(configuration.solver_constructor_name)
    if solver is None:
        raise NotImplementedError(f'{configuration.solver_constructor_name} not supported yet')

    return solver(configuration=configuration,
                  donors_dict=donors_dict,
                  recipients_dict=recipients_dict,
                  scorer=scorer)
