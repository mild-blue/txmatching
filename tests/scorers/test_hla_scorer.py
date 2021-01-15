import unittest

from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import HLATyping, PatientParameters
from txmatching.patients.patient_parameters_dataclasses import HLAType
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.enums import Country


class TestHlaScorer(unittest.TestCase):
    def test_scorer_on_some_patients(self):
        scorer = HLAAdditiveScorer()
        donor = Donor(
            db_id=1,
            medical_id='donor',
            parameters=PatientParameters(
                blood_group='A',
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
                blood_group='A',
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
                blood_group='A',
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
        self.assertEqual(4, scorer.score_transplant(donor=donor, recipient=recipient, original_donor=original_donor))
