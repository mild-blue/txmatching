from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Tuple

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.solvers.all_solutions_solver.scoring_utils import \
    get_score_for_idx_pairs
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.donor_recipient_pair_idx_only import \
    DonorRecipientPairIdxOnly
from txmatching.solvers.ilp_solver.txm_configuration_for_ilp import \
    DataAndConfigurationForILPSolver
from txmatching.solvers.matching.matching_with_score import MatchingWithScore


@dataclass(init=True)
class SolverBase:
    # pylint: disable=too-many-instance-attributes
    config_parameters: ConfigParameters
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]
    scorer: AdditiveScorer
    donors: List[Donor] = field(init=False)
    recipients: List[Recipient] = field(init=False)
    compatibility_graph: CompatibilityGraph = field(init=False)
    original_donor_idx_to_recipient_idx: Dict[int, int] = field(init=False)

    def __post_init__(self):
        self.donors = list(self.donors_dict.values())
        self.recipients = list(self.recipients_dict.values())
        self.compatibility_graph = self.scorer.get_compatibility_graph(
            self.recipients_dict,
            self.donors_dict
        )
        self.original_donor_idx_to_recipient_idx = self.scorer.get_original_donor_idx_to_recipient_idx(
            self.recipients_dict,
            self.donors_dict
        )
        self.required_donor_idxs_per_recipient_idx = self._get_required_donor_idxs_per_recipient_idx()

    def solve(self) -> Iterator[MatchingWithScore]:
        raise NotImplementedError('Has to be overridden')

    def solve_kepsoft(self, config_for_ilp_solver: DataAndConfigurationForILPSolver) -> List[List[Tuple[int, int]]]:
        raise NotImplementedError('Has to be overridden')

    def get_matching_from_path_combinations(
            self, found_pairs_idxs_only: List[DonorRecipientPairIdxOnly]) -> MatchingWithScore:
        found_pairs = frozenset(DonorRecipientPair(self.donors[found_pair_idxs_only.donor_idx],
                                                   self.recipients[found_pair_idxs_only.recipient_idx])
                                for found_pair_idxs_only in found_pairs_idxs_only)
        score = get_score_for_idx_pairs(self.compatibility_graph, found_pairs_idxs_only)
        return MatchingWithScore(found_pairs, score)

    def _get_required_donor_idxs_per_recipient_idx(self):
        donor_db_id_to_idx = {donor.db_id: i for i, donor in enumerate(self.donors_dict.values())}
        required_donor_idx = []
        for recipient_db_id in self.config_parameters.required_patient_db_ids:
            required_donor_idx_one_recipient = []
            for donor_db_id in self.recipients_dict[recipient_db_id].related_donors_db_ids:
                required_donor_idx_one_recipient.append(donor_db_id_to_idx[donor_db_id])
            if len(required_donor_idx_one_recipient) > 0:
                required_donor_idx.append(required_donor_idx_one_recipient)
        return required_donor_idx
