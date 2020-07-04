from kidney_exchange.solvers.matching.transplant_round import TransplantRound


class Sequence(TransplantRound):
    """
    Sequence of consecutive transplants that starts either with
    altruistic donor (i.e. someone who just wants to donate his kidney)
    or
    bridging donor (i.e. someone left from previous matching, whose recipient already got a kidney (for example from
        altruist), but who he did not give his to anyone
    """
    pass
