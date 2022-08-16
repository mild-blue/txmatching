from txmatching.optimizer.optimizer_return_object import DonorToRecipient, OptimizerReturn


def export_return_data() -> OptimizerReturn:
    cycle = {(1, 2): [6, 5, 4, 7], (2, 1): [3, 2, 1, 4]}
    statistics = {"number_of_found_cycles": 1, "number_of_found_transplants": 2}
    return OptimizerReturn(
        cycles_and_chains=[[
            DonorToRecipient(donor_id=pair[0],recipient_id=pair[1], score=score) for pair, score in cycle.items()
        ]],
        statistics=statistics
    )
