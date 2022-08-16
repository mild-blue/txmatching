from txmatching.optimizer.optimizer_return_object import CycleOrChain, DonorToRecipient, OptimizerReturn, Statistics


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
