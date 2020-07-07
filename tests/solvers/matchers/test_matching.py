from unittest import TestCase

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient_parameters import PatientParameters
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.solvers.matching.matching import Matching


class TestMatching(TestCase):
    test_donor = Donor("test_donor", PatientParameters(blood_group="A"))
    test_recipient = Recipient("test_recipient", PatientParameters(blood_group="B"),
                               related_donors=test_donor)
    test_donor2 = Donor("test_donor2", PatientParameters(blood_group="B"))
    test_recipient2 = Recipient("test_recipient2", PatientParameters(blood_group="A"),
                                related_donors=test_donor2)
    test_donor3 = Donor("test_donor3", PatientParameters(blood_group="A"))
    test_recipient3 = Recipient("test_recipient3", PatientParameters(blood_group="F"),
                                related_donors=test_donor3)
    test_matching = Matching(donor_recipient_list=[
        (test_donor, test_recipient2),
        (test_donor2, test_recipient),
        (test_donor3, test_recipient)
    ])

    def test_get_cycles(self):
        cycles = self.test_matching.get_cycles()
        cycles_ids = {tuple((d.patient_id, r.patient_id) for d, r in cycle._donor_recipient_list) for cycle in cycles}
        self.assertEqual(cycles_ids, {(('test_donor', 'test_recipient2'), ('test_donor2', 'test_recipient')),
                                      (('test_donor2', 'test_recipient'), ('test_donor', 'test_recipient2'))})

    def test_get_sequences(self):
        seqs = self.test_matching.get_sequences()
        seq_ids = {tuple((d.patient_id, r.patient_id) for d, r in seq._donor_recipient_list) for seq in seqs}
        self.assertEqual(seq_ids, {tuple([('test_donor3', 'test_recipient'),
                                          ('test_donor', 'test_recipient2'),
                                          ('test_donor2', 'test_recipient')])})
