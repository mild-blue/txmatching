from txmatching.solvers.matching.transplant_round import TransplantRound


class TransplantSequence(TransplantRound):
    """
    Sequence of consecutive transplants that starts either with
    non-directed donor (i.e. someone who just wants to donate his kidney)
    or
    bridging donor (i.e. someone left from previous matching, whose recipient already got a kidney (for example from
        non-directed), but who he did not give his to anyone
    """
    # TODO proc tady mame tenhle file?
