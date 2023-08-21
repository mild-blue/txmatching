from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack)
from tests.scorers.test_hla_scorer import _create_donor, _create_recipient
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAType
from txmatching.utils.enums import HLAGroup, MatchType
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, HLAMatch,
    get_detailed_compatibility_index)
from txmatching.utils.hla_system.hla_preparation_utils import create_hla_type


class TestHlaScorer(DbTests):
    def test_get_genotype(self):
        calculated_detailed_score = get_detailed_compatibility_index(donor_parameters_Joe.hla_typing,
                                                                     recipient_parameters_Jack.hla_typing)

        expected = [
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.A,
                donor_matches=[HLAMatch(create_hla_type('A23'), MatchType.BROAD),
                               HLAMatch(create_hla_type('A26'), MatchType.NONE)],
                recipient_matches=[HLAMatch(create_hla_type('A9'), MatchType.BROAD),
                                   HLAMatch(create_hla_type('A30'), MatchType.NONE)],
                group_compatibility_index=1.0),
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.B,
                donor_matches=[HLAMatch(create_hla_type('B62'), MatchType.BROAD),
                               HLAMatch(create_hla_type('B38'), MatchType.NONE)],
                recipient_matches=[HLAMatch(create_hla_type('B77'), MatchType.BROAD),
                                   HLAMatch(create_hla_type('B14'), MatchType.NONE)],
                group_compatibility_index=3.0),
            DetailedCompatibilityIndexForHLAGroup(
                hla_group=HLAGroup.DRB1,
                donor_matches=[HLAMatch(create_hla_type('DR4'), MatchType.SPLIT),
                               HLAMatch(create_hla_type('DR11'), MatchType.SPLIT)],
                recipient_matches=[HLAMatch(create_hla_type('DR4'), MatchType.SPLIT),
                                   HLAMatch(create_hla_type('DR11'), MatchType.SPLIT)],
                group_compatibility_index=18.0),
            DetailedCompatibilityIndexForHLAGroup(hla_group=HLAGroup.CW,
                                    donor_matches=[
                                        HLAMatch(hla_type=create_hla_type('CW9'),
                                                match_type=MatchType.NONE),
                                        HLAMatch(hla_type=create_hla_type('CW12'),
                                                match_type=MatchType.NONE)],
                                    recipient_matches=[], group_compatibility_index=0.0),
            DetailedCompatibilityIndexForHLAGroup(hla_group=HLAGroup.DP,
                                        donor_matches=[
                                            HLAMatch(hla_type=create_hla_type('DP2'),
                                                    match_type=MatchType.NONE),
                                            HLAMatch(hla_type=create_hla_type('DP10'),
                                                    match_type=MatchType.NONE)],
                                        recipient_matches=[], group_compatibility_index=0.0),
            DetailedCompatibilityIndexForHLAGroup(hla_group=HLAGroup.DQ,
                                                  donor_matches=[
                                                      HLAMatch(hla_type=create_hla_type('DQ7'),
                                                               match_type=MatchType.NONE),
                                                      HLAMatch(hla_type=create_hla_type('DQ8'),
                                                               match_type=MatchType.NONE)],
                                                  recipient_matches=[], group_compatibility_index=0.0),
            DetailedCompatibilityIndexForHLAGroup(hla_group=HLAGroup.OTHER_DR,
                                                  donor_matches=[
                                                      HLAMatch(hla_type=create_hla_type('DR52'),
                                                               match_type=MatchType.NONE),
                                                      HLAMatch(hla_type=create_hla_type('DR53'),
                                                               match_type=MatchType.NONE)],
                                                  recipient_matches=[], group_compatibility_index=0.0)
        ]
        self.maxDiff = None
        for expected_result, actual_result in zip(expected, calculated_detailed_score):
            self.assertSetEqual(set(expected_result.donor_matches), set(actual_result.donor_matches))
            self.assertSetEqual(set(expected_result.recipient_matches), set(actual_result.recipient_matches))

    def test_duplicate_hla_codes_shown_and_sorted_correctly(self):
        donor = _create_donor(['A2'])
        recipient = _create_recipient(['A1', 'A2'])

        calculated_detailed_score = get_detailed_compatibility_index(donor.parameters.hla_typing,
                                                                     recipient.parameters.hla_typing)
        self.assertEqual(2, len(calculated_detailed_score[0].recipient_matches))
        expected_matches = [
            HLAMatch(hla_type=HLAType(raw_code='A1', code=HLACode(None, 'A1', 'A1')), match_type=MatchType.NONE),
            HLAMatch(hla_type=HLAType(raw_code='A2', code=HLACode(None, 'A2', 'A2')), match_type=MatchType.SPLIT)
        ]

        self.assertListEqual(expected_matches, calculated_detailed_score[0].recipient_matches)

    def test_duplicate_hla_codes_shown_correctly_vol2(self):
        donor = _create_donor(['A1'])
        recipient = _create_recipient(['A1'])

        calculated_detailed_score = get_detailed_compatibility_index(donor.parameters.hla_typing,
                                                                     recipient.parameters.hla_typing)
        self.assertEqual(2, len(calculated_detailed_score[0].recipient_matches))

        expected_matches = [
            HLAMatch(hla_type=HLAType(raw_code='A1', code=HLACode(None, 'A1', 'A1')), match_type=MatchType.SPLIT),
            HLAMatch(hla_type=HLAType(raw_code='A1', code=HLACode(None, 'A1', 'A1')), match_type=MatchType.NONE)
        ]

        self.assertListEqual(expected_matches, calculated_detailed_score[0].recipient_matches)
