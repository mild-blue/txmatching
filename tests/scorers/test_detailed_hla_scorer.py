import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack)
from txmatching.patients.hla_model import HLAType, HLATyping
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.high_res_hla_additive_scorer import \
    HighResHLAAdditiveScorer
from txmatching.scorers.split_hla_additive_scorer import SplitHLAAdditiveScorer
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLAGroup, MatchTypes
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, HLAMatch,
    get_detailed_compatibility_index)


class TestHlaScorer(unittest.TestCase):

    def test_get_genotype(self):
        calculated_detailed_score = get_detailed_compatibility_index(donor_parameters_Joe.hla_typing,
                                                                     recipient_parameters_Jack.hla_typing)

        expected = [
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.A,
                donor_matches=[HLAMatch(HLAType('A23'), MatchTypes.BROAD),
                               HLAMatch(HLAType('A26'), MatchTypes.NONE)],
                recipient_matches=[HLAMatch(HLAType('A9'), MatchTypes.BROAD),
                                   HLAMatch(HLAType('A30'), MatchTypes.NONE)],
                group_compatibility_index=1.0),
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.B,
                donor_matches=[HLAMatch(HLAType('B62'), MatchTypes.BROAD),
                               HLAMatch(HLAType('B38'), MatchTypes.NONE)],
                recipient_matches=[HLAMatch(HLAType('B77'), MatchTypes.BROAD),
                                   HLAMatch(HLAType('B14'), MatchTypes.NONE)],
                group_compatibility_index=3.0),
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.DRB1,
                donor_matches=[HLAMatch(HLAType('DR4'), MatchTypes.SPLIT), HLAMatch(HLAType('DR11'), MatchTypes.SPLIT)],
                recipient_matches=[HLAMatch(HLAType('DR4'), MatchTypes.SPLIT),
                                   HLAMatch(HLAType('DR11'), MatchTypes.SPLIT)],
                group_compatibility_index=18.0),
            DetailedCompatibilityIndexForHLAGroup(hla_group=HLAGroup.Other,
                                                  donor_matches=[
                                                      HLAMatch(hla_type=HLAType('DR52'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('DR53'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('DQ7'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('DQ8'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('DP2'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('DP10'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('CW9'), match_type=MatchTypes.NONE),
                                                      HLAMatch(hla_type=HLAType('CW12'), match_type=MatchTypes.NONE)],
                                                  recipient_matches=[], group_compatibility_index=0.0)

        ]
        self.maxDiff = None
        for expected_result, actual_result in zip(expected, calculated_detailed_score):
            self.assertSetEqual(set(expected_result.donor_matches), set(actual_result.donor_matches))
            self.assertSetEqual(set(expected_result.recipient_matches), set(actual_result.recipient_matches))

    def test_scorers_on_some_patients(self):
        split_scorer = SplitHLAAdditiveScorer()
        high_res_scorer = HighResHLAAdditiveScorer()
        donor = Donor(
            db_id=1,
            medical_id='donor',
            parameters=donor_parameters_Joe
        )
        recipient = Recipient(
            db_id=1,
            acceptable_blood_groups=[],
            related_donor_db_id=1,
            medical_id='recipient',
            parameters=recipient_parameters_Jack
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

        # A9 - BROAD +1
        # B77 - BROAD +3
        # DR4, DR11 - SPLIT +9 +9
        self.assertEqual(22, split_scorer.score_transplant(donor=donor, recipient=recipient, original_donor=original_donor))

        # A9 - BROAD +1
        # B77 - BROAD +1
        # DR4, DR11 - SPLIT +2 +2
        self.assertEqual(6, high_res_scorer.score_transplant(donor=donor, recipient=recipient, original_donor=original_donor))
