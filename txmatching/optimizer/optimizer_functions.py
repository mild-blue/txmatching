from typing import Dict, List, Optional

from txmatching.configuration.configuration import Configuration
from txmatching.optimizer.optimizer_return_object import CycleOrChain, DonorToRecipient, OptimizerReturn, Statistics
from txmatching.optimizer.optimizer_request_object import Limitations, OptimizerConfiguration, Pair
from txmatching.patients.patient_types import DonorDbId
from txmatching.patients.patient import Donor


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


def get_optimizer_configuration(config: Optional[Configuration]) -> OptimizerConfiguration:
    limitations = Limitations(
        max_cycle_length=config.parameters.max_cycle_length if config else 4,
        max_chain_length=config.parameters.max_sequence_length if config else 4,
        custom_algorithm_settings={}
    )
    return OptimizerConfiguration(
        limitations=limitations,
        scoring=None
    )
