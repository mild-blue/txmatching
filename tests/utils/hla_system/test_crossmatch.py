import logging
import unittest
from typing import List

from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_hla_type,
                                                        create_hla_typing)
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibody
from txmatching.utils.enums import AntibodyMatchTypes, HLACrossmatchLevel
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatch, get_crossmatched_antibodies, is_positive_hla_crossmatch)

logger = logging.getLogger(__name__)


class TestCrossmatch(unittest.TestCase):

    def _assert_positive_crossmatch(self, hla_type: str, hla_antibodies: List[HLAAntibody], use_high_resolution: bool,
                                    crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE):
        self.assertTrue(
            is_positive_hla_crossmatch(
                create_hla_typing(hla_types_list=[hla_type]),
                create_antibodies(hla_antibodies_list=hla_antibodies),
                use_high_resolution,
                crossmatch_level
            ), f'{hla_type} and {hla_antibodies} has NEGATIVE crossmatch (use_high_resolution={use_high_resolution})'
        )

    def _assert_negative_crossmatch(self, hla_type_raw: str, hla_antibodies: List[HLAAntibody],
                                    use_high_resolution: bool,
                                    crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE):
        self.assertFalse(
            is_positive_hla_crossmatch(
                create_hla_typing(hla_types_list=[hla_type_raw]),
                create_antibodies(hla_antibodies_list=hla_antibodies),
                use_high_resolution,
                crossmatch_level
            ),
            f'{hla_type_raw} and {hla_antibodies} has POSITIVE crossmatch (use_high_resolution={use_high_resolution})'
        )

    def _assert_raw_code_equal(self, raw_code: str, expected_hla_code: HLACode):
        actual_hla_code = create_hla_type(raw_code).code
        self.assertEqual(expected_hla_code, actual_hla_code)

    def test_crossmatch_split(self):
        """
        Checks if there is any crossmatch with high res crossmatch turn off
        """
        self._assert_raw_code_equal('A23', HLACode(None, 'A23', 'A9'))
        self._assert_raw_code_equal('A24', HLACode(None, 'A24', 'A9'))
        self._assert_raw_code_equal('A9', HLACode(None, None, 'A9'))
        self._assert_raw_code_equal('A1', HLACode(None, 'A1', 'A1'))
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        self._assert_positive_crossmatch('A9', [create_antibody('A9', 2100, 2000)], False)
        self._assert_negative_crossmatch('A9', [create_antibody('A9', 1900, 2000)], False)

        self._assert_negative_crossmatch('A23', [create_antibody('A24', 2100, 2000)], False)

        # broad crossmatch
        self._assert_positive_crossmatch('A9', [create_antibody('A23', 2100, 2000)], False)
        self._assert_negative_crossmatch('A9', [create_antibody('A1', 2100, 2000)], False)

        # with high res code specified:

        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:04', 2100, 2000)], False)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*24:02', 2100, 2000)], False)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:04', [create_antibody('A23', 2100, 2000)], False)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A24', 2100, 2000)], False)

        # split crossmatch with multiple antibodies:

        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], False)
        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A23', 2100, 2000)], False)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A23', 1900, 2000)], False)

    def test_crossmatch_high_res(self):
        """
        Checks if there is any crossmatch with high res crossmatch turn on
        """
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # mfi > cutoff:

        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:01', 2100, 2000)], True)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:04', 2100, 2000)], True)
        # positive split crossmatch
        self._assert_positive_crossmatch('A23', [create_antibody('A*23:04', 2100, 2000)], True)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:04', [create_antibody('A23', 2100, 2000)], True)
        # positive split crossmatch
        self._assert_positive_crossmatch('A23', [create_antibody('A23', 2100, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A24', [create_antibody('A*23:04', 2100, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A24', 2100, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A24', 2100, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*24:02', 2100, 2000)], True)

        # mfi < cutoff:

        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*23:01', 1900, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A*23:04', 1900, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A23', 1900, 2000)], True)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A23', 1900, 2000)], True)

        # multiple antibodies

        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 2100, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True)
        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A23', 2100, 2000)], True)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A23', 2100, 2000)], True)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:04', 1900, 2000),
                                          create_antibody('A23', 2100, 2000)], True)

    def _assert_matches_equal(self,
                              hla_type: str, hla_antibodies: List[HLAAntibody],
                              use_high_resolution: bool,
                              expected_antibody_matches: List[AntibodyMatch]):
        crossmatched_antibodies = get_crossmatched_antibodies(
            create_hla_typing(hla_types_list=[hla_type]),
            create_antibodies(hla_antibodies_list=hla_antibodies),
            use_high_resolution
        )

        actual_antibody_matches = [antibody_match for match_group in crossmatched_antibodies
                                   for antibody_match in match_group.antibody_matches]

        self.assertCountEqual(expected_antibody_matches, actual_antibody_matches)

    def test_get_crossmatched_antibodies(self):
        """
        Also checks the matches that the get_crossmatched_antibodies function returns.
        """
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # mfi > cutoff:

        # positive high res crossmatch
        self._assert_matches_equal('A*23:01', [create_antibody('A*23:01', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2100, 2000), AntibodyMatchTypes.HIGH_RES)])
        # positive split crossmatch
        self._assert_matches_equal('A*23:01', [create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:04', 2100, 2000), AntibodyMatchTypes.HIGH_RES)])
        # negative split crossmatch
        self._assert_matches_equal('A*23:01', [create_antibody('A*24:02', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*24:02', 2100, 2000), AntibodyMatchTypes.NONE)])

        # mfi < cutoff:

        # negative high res crossmatch
        self._assert_matches_equal('A*01:01', [create_antibody('A*23:01', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2100, 2000), AntibodyMatchTypes.NONE)])

        # multiple antibodies

        # positive high res crossmatch
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2100, 2000), AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody('A*23:04', 2100, 2000), AntibodyMatchTypes.NONE)])
        # negative high res crossmatch
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:04', 2100, 2000), AntibodyMatchTypes.NONE)])
        # positive split crossmatch
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A23', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A23', 2100, 2000), AntibodyMatchTypes.HIGH_RES)])
        # negative high res crossmatch
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A23', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A23', 2100, 2000), AntibodyMatchTypes.NONE)])

    def test_antibodies_with_multiple_mfis(self):
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # split matches:

        # first matching antibody with mfi > cutoff, second with mfi < cutoff
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2100, 2000), AntibodyMatchTypes.SPLIT)])
        # first matching antibody with mfi < cutoff, second with mfi > cutoff
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:04', 2100, 2000), AntibodyMatchTypes.SPLIT)])
        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2100, 2000), AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody('A*23:04', 2200, 2000), AntibodyMatchTypes.HIGH_RES)])
        # first matching antibody with mfi1 > cutoff, second with mfi2 < mfi1
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2200, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2200, 2000), AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody('A*23:04', 2100, 2000), AntibodyMatchTypes.HIGH_RES)])
        # first matching antibody with mfi < cutoff, second with mfi < cutoff
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 1800, 2000)], True,
                                   [])

        # high res match

        # antibodies duplicity should not raise duplicity assert, because the antibodies are joined before creating
        # antibodies per groups. Instead, mean mfi is computed.
        # first matching antibody with mfi < cutoff, second with mfi > cutoff
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:01', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2050, 2000), AntibodyMatchTypes.HIGH_RES)])
        # antibodies duplicity should not raise duplicity assert, because the antibodies are joined before creating
        # antibodies per groups. Instead, mean mfi is computed.
        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:01', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody('A*23:01', 2150, 2000), AntibodyMatchTypes.HIGH_RES)])

        # broad matches:

        # first matching antibody with mfi < cutoff, second with mfi > cutoff
        self._assert_matches_equal('A9',
                                   [create_antibody('A9', 1900, 2000),
                                    create_antibody('A9', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody('A9', 2000, 2000), AntibodyMatchTypes.HIGH_RES)])
        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1
        self._assert_matches_equal('A9',
                                   [create_antibody('A9', 2100, 2000),
                                    create_antibody('A9', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody('A9', 2150, 2000), AntibodyMatchTypes.HIGH_RES)])

    def test_crossmatch_level(self):
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertFalse(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertTrue(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertFalse(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertFalse(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.NONE))

    def test_virtual_crossmatch_if_all_antibodies_positive_in_high_res(self):
        high_res_antibodies_all_positive = [create_antibody('A*24:02', 2100, 2000),
                                            create_antibody('A*23:01', 2100, 2000),
                                            create_antibody('A*23:04', 2100, 2000)]
        high_res_antibodies_not_all_positive = [create_antibody('A*24:02', 1900, 2000),
                                                create_antibody('A*23:01', 2100, 2000),
                                                create_antibody('A*23:04', 2100, 2000)]

        self._assert_negative_crossmatch('A9', high_res_antibodies_not_all_positive, True, HLACrossmatchLevel.BROAD)

        self._assert_positive_crossmatch('A9', high_res_antibodies_all_positive, True, HLACrossmatchLevel.BROAD)

        self._assert_positive_crossmatch('A9', high_res_antibodies_not_all_positive, True, HLACrossmatchLevel.NONE)

        self._assert_positive_crossmatch('A9', high_res_antibodies_all_positive, True, HLACrossmatchLevel.NONE)

        self._assert_negative_crossmatch('A23',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         HLACrossmatchLevel.SPLIT_AND_BROAD)

        self._assert_positive_crossmatch('A23',
                                         [create_antibody('A*23:01', 2100, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         HLACrossmatchLevel.SPLIT_AND_BROAD)
