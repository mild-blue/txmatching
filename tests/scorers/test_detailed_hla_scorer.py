import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack)
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import (HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.scorers.hla_additive_scorer import HLAAdditiveScorer
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, HLAGroups, MatchTypes
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, compatibility_index_detailed)


class TestHlaScorer(unittest.TestCase):

    def test_get_genotype(self):
        calculated_detailed_score = compatibility_index_detailed(donor_parameters_Joe.hla_typing,
                                                                 recipient_parameters_Jack.hla_typing)

        expected = {
            HLAGroups.A: DetailedCompatibilityIndexForHLAGroup(donor_matches={'A23': MatchTypes.BROAD},
                                                               recipient_matches={'A9': MatchTypes.BROAD},
                                                               group_compatibility_index=1.0),
            HLAGroups.B: DetailedCompatibilityIndexForHLAGroup(donor_matches={'B62': MatchTypes.BROAD},
                                                               recipient_matches={'B77': MatchTypes.BROAD},
                                                               group_compatibility_index=3.0),
            HLAGroups.DRB1: DetailedCompatibilityIndexForHLAGroup(
                donor_matches={'DR4': MatchTypes.SPLIT, 'DR11': MatchTypes.BROAD},
                recipient_matches={'DR4': MatchTypes.SPLIT, 'DR11': MatchTypes.BROAD}, group_compatibility_index=18.0)}
        self.maxDiff = None
        self.assertDictEqual(expected, calculated_detailed_score)

    def test_scorer_on_some_patients(self):
        scorer = HLAAdditiveScorer()
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
        self.assertEqual(4, scorer.score_transplant(donor=donor, recipient=recipient, original_donor=original_donor))
