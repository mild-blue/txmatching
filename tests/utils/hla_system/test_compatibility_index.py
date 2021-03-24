import logging
import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack,
                                                    recipient_parameters_Wrong)
from tests.test_utilities.hla_preparation_utils import (create_hla_type,
                                                        create_hla_typing)
from txmatching.scorers.high_res_hla_additive_scorer import \
    HighResScorerCIConfiguration
from txmatching.scorers.split_hla_additive_scorer import \
    SplitScorerCIConfiguration
from txmatching.utils.enums import MatchType
from txmatching.utils.hla_system.compatibility_index import (
    HLAMatch, compatibility_index, get_detailed_compatibility_index)

logger = logging.getLogger(__name__)
DR_INDEX = 2
OTHER_INDEX = 3
A_INDEX = 0


class TestCompatibilityIndex(unittest.TestCase):
    def setUp(self):
        self._donor_recipient_index = [
            (donor_parameters_Joe, recipient_parameters_Jack, 22.0, 6.0),
            (donor_parameters_Joe, recipient_parameters_Wrong, 22.0, 6.0)
        ]

    def test_compatibility_index(self):
        for donor_params, recipient_params, expected_ci_split, expected_ci_high_res in self._donor_recipient_index:
            calculated_ci_split = compatibility_index(donor_params.hla_typing,
                                                      recipient_params.hla_typing,
                                                      ci_configuration=SplitScorerCIConfiguration())
            calculated_ci_high_res = compatibility_index(donor_params.hla_typing,
                                                         recipient_params.hla_typing,
                                                         ci_configuration=HighResScorerCIConfiguration())
            self.assertEqual(expected_ci_split, calculated_ci_split)
            self.assertEqual(expected_ci_high_res, calculated_ci_high_res)

    def test_compatibility_index_with_high_res(self):
        ci = get_detailed_compatibility_index(
            create_hla_typing(
                ['DRB1*04:01', 'DRB1*07:01']
            ),
            create_hla_typing(
                ['DRB1*04:02', 'DRB1*07:01']
            )
        )

        expected = {HLAMatch(hla_type=create_hla_type(raw_code='DRB1*04:02'), match_type=MatchType.SPLIT),
                    HLAMatch(hla_type=create_hla_type(raw_code='DRB1*07:01'), match_type=MatchType.HIGH_RES)}

        self.assertSetEqual(expected, set(ci[DR_INDEX].recipient_matches))

        ci = get_detailed_compatibility_index(
            create_hla_typing(
                ['C*12:03', 'DRB3*01:01',
                 'DQA1*03:01', 'DQB1*06:03',
                 'DQB1*03:02', 'DPB1*02:01']
            ),
            create_hla_typing(
                ['C*04:01', 'DQA1*02:01',
                 'DQB1*03:03', 'DQB1*05:01',
                 'DPB1*04:01', 'DPB1*09:01']
            )
        )

        expected = {HLAMatch(hla_type=create_hla_type(raw_code='C*04:01'), match_type=MatchType.NONE),
                    HLAMatch(hla_type=create_hla_type(raw_code='DQA1*02:01'), match_type=MatchType.NONE),
                    HLAMatch(hla_type=create_hla_type(raw_code='DPB1*09:01'), match_type=MatchType.NONE),
                    HLAMatch(hla_type=create_hla_type(raw_code='DQB1*03:03'), match_type=MatchType.BROAD),
                    HLAMatch(hla_type=create_hla_type(raw_code='DQB1*05:01'), match_type=MatchType.BROAD),
                    HLAMatch(hla_type=create_hla_type(raw_code='DPB1*04:01'), match_type=MatchType.NONE)
                    }

        self.assertSetEqual(expected, set(ci[OTHER_INDEX].recipient_matches))

        ci = get_detailed_compatibility_index(
            create_hla_typing(
                ['A*23:04']
            ),
            create_hla_typing(
                ['A*23:01']
            )
        )

        expected = {HLAMatch(hla_type=create_hla_type(raw_code='A*23:01'), match_type=MatchType.SPLIT)}

        self.assertSetEqual(expected, set(ci[A_INDEX].recipient_matches))

        ci = get_detailed_compatibility_index(
            create_hla_typing(
                ['A*23:04']

            ),
            create_hla_typing(
                ['A*24:02']

            ),
        )

        expected = {HLAMatch(hla_type=create_hla_type(raw_code='A*24:02'), match_type=MatchType.BROAD)}

        self.assertSetEqual(expected, set(ci[A_INDEX].recipient_matches))

        expected = {HLAMatch(hla_type=create_hla_type(raw_code='A*23:04'), match_type=MatchType.BROAD)}

        self.assertSetEqual(expected, set(ci[A_INDEX].donor_matches))
