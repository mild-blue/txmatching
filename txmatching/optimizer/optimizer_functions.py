from typing import Dict, List, Optional

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.optimizer.optimizer_return_object import CycleOrChain, DonorToRecipient, OptimizerReturn, Statistics
from txmatching.optimizer.optimizer_request_object import Limitations, OptimizerConfiguration, Pair
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.split_hla_additive_scorer import SplitScorer


def export_return_data() -> OptimizerReturn:
    cycle = {(1, 2): [6, 5, 4, 7], (2, 1): [3, 2, 1, 4]}
    donor_to_recipient_list = [DonorToRecipient(donor_id=pair[0], recipient_id=pair[1], score=score) for pair, score in
                               cycle.items()]
    return OptimizerReturn(
        cycles_and_chains=[
            CycleOrChain(donor_to_recipient_list, [1, 2, 5])
        ],
        statistics=Statistics(1, 2)
    )


def get_pairs_from_txm_event(donors: Dict[DonorDbId, Donor]) -> List[Pair]:
    pairs = [Pair(donor_id=donor_id, recipient_id=donor.related_recipient_db_id) for donor_id, donor in donors.items()]
    return pairs


def get_optimizer_configuration(config: Optional[ConfigParameters]) -> OptimizerConfiguration:
    limitations = Limitations(
        max_cycle_length=config.max_cycle_length if config else 4,
        max_chain_length=config.max_sequence_length if config else 4,
        custom_algorithm_settings={}
    )
    # todo: I don't actually know what the number represents? this is a temporary scoring
    scoring = [[{"hla_compatibility_score": 1}]]
    return OptimizerConfiguration(
        limitations=limitations,
        scoring=scoring
    )


def get_compatibility_graph(donors: Dict[DonorDbId, Donor], recipients: Dict[RecipientDbId, Recipient]) -> List[
    Dict[str, int]]:
    scorer = SplitScorer()

    score_matrix = scorer.get_score_matrix(recipients, donors)

    compatibility_graph = []
    for i, donor_id in enumerate(donors):
        for j, recipient_id in enumerate(recipients):
            comp_graph_cell = {
                "donor_id": donor_id,
                "recipient_id": recipient_id,
                "hla_compatibility_score": int(score_matrix[i][j])
            }
            compatibility_graph.append(comp_graph_cell)
    return compatibility_graph
