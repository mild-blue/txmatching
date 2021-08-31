from typing import Dict

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.solvers.all_solutions_solver.all_solutions_solver import \
    AllSolutionsSolver
from txmatching.solvers.ilp_solver.ilp_solver import ILPSolver
from txmatching.solvers.solver_base import SolverBase

SUPPORTED_SOLVERS = [AllSolutionsSolver, ILPSolver]


def solver_from_configuration(config_parameters: ConfigParameters,
                              donors_dict: Dict[DonorDbId, Donor],
                              recipients_dict: Dict[RecipientDbId, Recipient],
                              scorer: AdditiveScorer) -> SolverBase:
    solver_dict = {supported_object.__name__: supported_object for supported_object in SUPPORTED_SOLVERS}
    solver = solver_dict.get(config_parameters.solver_constructor_name)
    if solver is None:
        raise NotImplementedError(f'{config_parameters.solver_constructor_name} not supported yet')

    return solver(config_parameters=config_parameters,
                  donors_dict=donors_dict,
                  recipients_dict=recipients_dict,
                  scorer=scorer)
