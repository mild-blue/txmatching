import unittest

from txmatching.patients.hla_model import HLAType, HLATyping
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.high_res_hla_additive_scorer import \
    HighResHLAAdditiveScorer
from txmatching.scorers.split_hla_additive_scorer import SplitHLAAdditiveScorer
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country


class TestHlaScorer(unittest.TestCase):
    def test_scorers_on_some_patients(self):
        split_scorer = SplitHLAAdditiveScorer()
        high_res_scorer = HighResHLAAdditiveScorer()
        donor = Donor(
            db_id=1,
            medical_id='donor',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    [HLAType('A1'),
                     HLAType('A3'),
                     HLAType('B7'),
                     HLAType('B37'),
                     HLAType('DR11'),
                     HLAType('DR15'),
                     HLAType('DR52'),
                     HLAType('DR51'),
                     HLAType('DQ7'),
                     HLAType('DQ6')]
                )

            )
        )
        recipient = Recipient(
            db_id=1,
            acceptable_blood_groups=[],
            related_donor_db_id=1,
            medical_id='recipient',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    [HLAType('A1'),
                     HLAType('A2'),
                     HLAType('B27'),
                     HLAType('B37'),
                     HLAType('DR1'),
                     HLAType('DR10')]
                )
            )
        )

        original_donor = Donor(
            db_id=2,
            medical_id='original_donor',
            related_recipient_db_id=1,
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    [HLAType('A1'),
                     HLAType('A9'),
                     HLAType('B7'),
                     HLAType('B37'),
                     HLAType('DR11'),
                     HLAType('DR15'),
                     HLAType('DR52'),
                     HLAType('DR51'),
                     HLAType('DQ7'),
                     HLAType('DQ6')]
                )
            )
        )

        self.assertEqual(4, split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                          original_donor=original_donor))
        self.assertEqual(4, high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                             original_donor=original_donor))
