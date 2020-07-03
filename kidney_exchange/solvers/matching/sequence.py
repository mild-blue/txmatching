from kidney_exchange.solvers.matching.round import Round


class Sequence(Round):
    """
    Sequence of consequtive transplants that starts either with
    altruistic donor: just wants to give someone his kidney
    or
    bridging donor: someone who is left from previous matching, his recipient got kidney (for example from altruist)
        but he did not give his to anyone
    """
    pass
