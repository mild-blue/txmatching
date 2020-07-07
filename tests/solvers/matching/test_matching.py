from unittest import TestCase

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


def _create_recipient(id: str, donor: Donor):
    return Recipient(id, related_donors=donor)


class TestMatching(TestCase):
    d1 = Donor("d1")
    d2 = Donor("d2")
    d3 = Donor("d3")
    d4 = Donor("d4")
    d5 = Donor("d5")
    d6 = Donor("d6")
    d7 = Donor("d7")
    d8 = Donor("d8")

    r1 = _create_recipient("r1", d1)
    r2 = _create_recipient("r2", d2)
    r3 = _create_recipient("r3", d3)
    r4 = _create_recipient("r4", d4)
    r5 = _create_recipient("r5", d5)
    r6 = _create_recipient("r6", d6)
    r7 = _create_recipient("r7", d7)
    r8 = _create_recipient("r8", d8)
    drl = [
        (d1, r2),
        (d2, r3),
        (d3, r4),
        (d4, r1),
        (d5, r6),
        (d6, r7),
        (d8, r8)
    ]
    rnd_shuffle = [4, 1, 0, 5, 6, 2, 3]

    def test_get_cycles(self):
        drl_shuffled = [self.drl[i] for i in self.rnd_shuffle]
        test_matching = Matching(donor_recipient_list=drl_shuffled)
        cycles = test_matching.get_cycles()
        cycles_ids = {tuple((d.patient_id, r.patient_id) for d, r in cycle._donor_recipient_list) for cycle in cycles}
        exp = {(('d8', 'r8'),), (('d2', 'r3'), ('d3', 'r4'), ('d4', 'r1'), ('d1', 'r2'))}
        self.assertEqual(exp, cycles_ids)

    def test_get_sequences(self):
        drl_shuffled = [self.drl[i] for i in self.rnd_shuffle]
        test_matching = Matching(donor_recipient_list=drl_shuffled)
        seqs = test_matching.get_sequences()
        seq_ids = {tuple((d.patient_id, r.patient_id) for d, r in seq._donor_recipient_list) for seq in seqs}
        self.assertEqual(seq_ids, {(('d5', 'r6'), ('d6', 'r7'))})
