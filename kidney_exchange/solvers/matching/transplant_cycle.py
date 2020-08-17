from kidney_exchange.solvers.matching.transplant_round import TransplantRound


class TransplantCycle(TransplantRound):
    """
    Set of consecutive transplants that starts with donor of some pair X and ends with recipient of pair X
    """
