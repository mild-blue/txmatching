import unittest

from tests.test_utilities.hla_preparation_utils import get_hla_typing
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
                hla_typing=get_hla_typing(
                    ['A1',
                     'A3',
                     'B7',
                     'B37',
                     'DR11',
                     'DR15',
                     'DR52',
                     'DR51',
                     'DQ7',
                     'DQ6']
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
                hla_typing=get_hla_typing(
                    ['A1',
                     'A2',
                     'B27',
                     'B37',
                     'DR1',
                     'DR10']
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
                hla_typing=get_hla_typing(
                    ['A1',
                     'A9',
                     'B7',
                     'B37',
                     'DR11',
                     'DR15',
                     'DR52',
                     'DR51',
                     'DQ7',
                     'DQ6']
                )
            )
        )

        self.assertEqual(4, split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                          original_donor=original_donor))
        self.assertEqual(4, high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                             original_donor=original_donor))
