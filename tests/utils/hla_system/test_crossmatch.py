import logging
import os
import unittest
from typing import Callable, List

from local_testing_utilities.generate_patients import LARGE_DATA_FOLDER
from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_antibody_parsed,
                                                        create_hla_type,
                                                        create_hla_typing)
from tests.utils.hla_system.type_a_example_recipient import TYPE_A_EXAMPLE_REC
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import HLAAntibodyRaw
from txmatching.utils.enums import (AntibodyMatchTypes, HLAAntibodyType,
                                    HLACrossmatchLevel)
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatch, do_crossmatch_in_type_a, do_crossmatch_in_type_b,
    is_positive_hla_crossmatch, is_recipient_type_a)

logger = logging.getLogger(__name__)


class TestCrossmatch(unittest.TestCase):

    def _assert_positive_crossmatch(self,
                                    hla_type: str,
                                    hla_antibodies: List[HLAAntibodyRaw],
                                    use_high_resolution: bool,
                                    crossmatch_logic: Callable,
                                    crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE):
        self.assertTrue(
            is_positive_hla_crossmatch(
                create_hla_typing(hla_types_list=[hla_type]),
                create_antibodies(hla_antibodies_list=hla_antibodies),
                use_high_resolution,
                crossmatch_level,
                crossmatch_logic
            ), f'{hla_type} and {hla_antibodies} has NEGATIVE crossmatch ({use_high_resolution = })'
        )

    def _assert_negative_crossmatch(self,
                                    hla_type: str,
                                    hla_antibodies: List[HLAAntibodyRaw],
                                    use_high_resolution: bool,
                                    crossmatch_logic: Callable,
                                    crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE):
        self.assertFalse(
            is_positive_hla_crossmatch(
                create_hla_typing(hla_types_list=[hla_type]),
                create_antibodies(hla_antibodies_list=hla_antibodies),
                use_high_resolution,
                crossmatch_level,
                crossmatch_logic
            ),
            f'{hla_type} and {hla_antibodies} has POSITIVE crossmatch ({use_high_resolution = })'
        )

    def _assert_raw_code_equal(self, raw_code: str, expected_hla_code: HLACode):
        actual_hla_code = create_hla_type(raw_code).code
        self.assertEqual(expected_hla_code, actual_hla_code)

    def test_is_recipient_type_a(self):
        with open(os.path.join(LARGE_DATA_FOLDER, 'high_res_example_data_CZE.json')) as f:
            import json
            data = json.load(f)

            antibodies = [create_antibody(antibody_json['name'], antibody_json['mfi'], antibody_json['cutoff'])
                          for antibody_json in data['recipients'][0]['hla_antibodies']]

        # all criteria are fulfilled
        self.assertTrue(is_recipient_type_a(create_antibodies(antibodies)))

        # not all antibodies are in high resolution
        antibodies[0] = create_antibody('A9', 1900, 2000)
        self.assertFalse(is_recipient_type_a(create_antibodies(antibodies)))

        # there is less than `MINIMUM_REQUIRED_ANTIBODIES_FOR_TYPE_A`
        antibodies[0] = create_antibody('A*23:01', 2000, 2100)  # negative antibody to fulfill general criteria
        self.assertFalse(is_recipient_type_a(create_antibodies(antibodies[:15])))

        # there is no antibody below the cutoff
        antibodies = [
            antibody if antibody.mfi > antibody.cutoff else create_antibody(antibody.raw_code, antibody.cutoff * 2,
                                                                            antibody.cutoff) for antibody in antibodies]
        self.assertFalse(is_recipient_type_a(create_antibodies(antibodies)))

        self.assertTrue(is_recipient_type_a(create_antibodies(TYPE_A_EXAMPLE_REC)))

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

        self._assert_positive_crossmatch('A9', [create_antibody('A9', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        self._assert_negative_crossmatch('A9', [create_antibody('A9', 1900, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        self._assert_negative_crossmatch('A23', [create_antibody('A24', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        # broad crossmatch
        self._assert_positive_crossmatch('A9', [create_antibody('A23', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        self._assert_negative_crossmatch('A9', [create_antibody('A1', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        # with high res code specified:

        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:04', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_a)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*24:02', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:04', [create_antibody('A23', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A24', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        # split crossmatch with multiple antibodies:

        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_a)
        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A23', 2100, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A23', 1900, 2000)], False,
                                         crossmatch_logic=do_crossmatch_in_type_b)

    def test_crossmatch_high_res(self):
        """
        Checks if there is any crossmatch with high res crossmatch turn on
        """
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # mfi > cutoff:

        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:01', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01', [create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_a)
        # positive split crossmatch
        self._assert_positive_crossmatch('A23', [create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:04', [create_antibody('A23', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # positive split crossmatch
        self._assert_positive_crossmatch('A23', [create_antibody('A23', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A24', [create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A24', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A24', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*24:02', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        # mfi < cutoff:

        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01', [create_antibody('A*23:01', 1900, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A*23:04', 1900, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A*23:04', [create_antibody('A23', 1900, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative split crossmatch
        self._assert_negative_crossmatch('A23', [create_antibody('A23', 1900, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)

        # multiple antibodies

        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 2100, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # positive high res crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A23', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)
        # negative high res crossmatch
        self._assert_negative_crossmatch('A*23:01',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_a)
        # positive split crossmatch
        self._assert_positive_crossmatch('A*23:01',
                                         [create_antibody('A*23:04', 1900, 2000),
                                          create_antibody('A23', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_b)

    def test_undecidable(self):
        # Antibody undecidable in type A
        hla_antibodies = [create_antibody('DQB1*04:02', 2100, 2000)]
        res = do_crossmatch_in_type_a(create_hla_typing(hla_types_list=[]),
                                      create_antibodies(hla_antibodies_list=hla_antibodies),
                                      use_high_resolution=True)
        self.assertEqual(AntibodyMatchTypes.UNDECIDABLE, res[5].antibody_matches[0].match_type)

        # Antibody undecidable in type B
        hla_antibodies = [create_antibody('DQ6', 2100, 2000)]
        res = do_crossmatch_in_type_b(create_hla_typing(hla_types_list=[]),
                                      create_antibodies(hla_antibodies_list=hla_antibodies),
                                      use_high_resolution=True)

        self.assertEqual(AntibodyMatchTypes.UNDECIDABLE, res[5].antibody_matches[0].match_type)

        # Antibody below cutoff, should not be returned in type a
        hla_antibodies = [create_antibody('DQB1*04:02', 1900, 2000)]
        res = do_crossmatch_in_type_a(create_hla_typing(hla_types_list=[]),
                                      create_antibodies(hla_antibodies_list=hla_antibodies),
                                      use_high_resolution=True)

        self.assertEqual([], res[5].antibody_matches)

        # Antibody below cutoff, should not be returned in type b
        hla_antibodies = [create_antibody('DQ6', 1900, 2000)]
        res = do_crossmatch_in_type_b(create_hla_typing(hla_types_list=[]),
                                      create_antibodies(hla_antibodies_list=hla_antibodies),
                                      use_high_resolution=True)

        self.assertEqual([], res[5].antibody_matches)

    def test_theoretical(self):
        # Antibody theoretical in type A
        hla_antibodies = create_antibodies(hla_antibodies_list=[create_antibody('A*23:01', 2100, 2000)])
        hla_antibodies.hla_antibodies_per_groups[0].hla_antibody_list[0].type = HLAAntibodyType.THEORETICAL
        res = do_crossmatch_in_type_a(create_hla_typing(hla_types_list=['A*23:01', 'B*04:03']),
                                      hla_antibodies,
                                      use_high_resolution=True)

        self.assertEqual(AntibodyMatchTypes.THEORETICAL, res[0].antibody_matches[0].match_type)

        # Antibody theoretical in type B
        hla_antibodies = create_antibodies(hla_antibodies_list=[create_antibody('B*07:70', 2100, 2000)])
        hla_antibodies.hla_antibodies_per_groups[1].hla_antibody_list[0].type = HLAAntibodyType.THEORETICAL

        res = do_crossmatch_in_type_b(create_hla_typing(hla_types_list=['A*02:01', 'B*07:70']),
                                      hla_antibodies,
                                      use_high_resolution=True)

        self.assertEqual(AntibodyMatchTypes.THEORETICAL, res[1].antibody_matches[0].match_type)

    def _assert_matches_equal(self,
                              hla_type: str, hla_antibodies: List[HLAAntibodyRaw],
                              use_high_resolution: bool,
                              expected_antibody_matches: List[AntibodyMatch],
                              is_type_a: bool):
        # False -> 0 | True -> 1
        crossmatch_type_functions = [do_crossmatch_in_type_b, do_crossmatch_in_type_a]
        crossmatched_antibodies = crossmatch_type_functions[is_type_a](
            create_hla_typing(hla_types_list=[hla_type]),
            create_antibodies(hla_antibodies_list=hla_antibodies),
            use_high_resolution
        )

        actual_antibody_matches = [antibody_match for match_group in crossmatched_antibodies
                                   for antibody_match in match_group.antibody_matches]

        self.assertCountEqual(expected_antibody_matches, actual_antibody_matches)

    def test_get_crossmatched_antibodies(self):
        """
        Checks the matches that the `get_crossmatched_antibodies` function returns.
        """

        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # mfi > cutoff:

        # positive high res crossmatch  # HIGH_RES_1
        self._assert_matches_equal('A*23:01', [create_antibody('A*23:01', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=False)

        # positive high res crossmatch for special case of C*04:03 from exceptions
        self._assert_matches_equal('CW6', [create_antibody('C*04:03', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('CW6', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('CW4', 2100, 2000),
                                                  AntibodyMatchTypes.NONE)],
                                   is_type_a=True)
        # positive high res crossmatch for special case of C*04:03 from exceptions
        self._assert_matches_equal('C*04:03', [create_antibody('C*04:03', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('CW6', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('CW4', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=True)

    def test_antibodies_with_multiple_mfis(self):
        self._assert_raw_code_equal('A*23:01', HLACode('A*23:01', 'A23', 'A9'))
        self._assert_raw_code_equal('A*23:04', HLACode('A*23:04', 'A23', 'A9'))
        self._assert_raw_code_equal('A*24:02', HLACode('A*24:02', 'A24', 'A9'))

        # high res matches:

        # antibodies duplicity should not raise duplicity assert, because the antibodies are joined before creating
        # antibodies per groups. Instead, mean mfi is computed.
        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # HIGH_RES_1
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:01', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2050, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=False)
        # antibodies duplicity should not raise duplicity assert, because the antibodies are joined before creating
        # antibodies per groups. Instead, mean mfi is computed.
        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1  # HIGH_RES_1
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:01', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2150, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=False)

        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1  # HIGH_RES_2
        self._assert_matches_equal('A*24:02',
                                   [create_antibody('A*24:37', 2100, 2000),
                                    create_antibody('A*24:85', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*24:37', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('A*24:85', 2200, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=True)

        # first matching antibody with mfi1 > cutoff, second with mfi2 > mfi1  # HIGH_RES_3
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 2200, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('A*23:04', 2200, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=True)
        # first matching antibody with mfi1 > cutoff, second with cutoff < mfi2 < mfi1  # HIGH_RES_3
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2200, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2200, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('A*23:04', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES)],
                                   is_type_a=True)

        # split matches:

        # first matching antibody with mfi > cutoff, second with mfi < cutoff  # SPLIT_1
        self._assert_matches_equal('A23',
                                   [create_antibody('A23', 2100, 2000),
                                    create_antibody('A*23:04', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A23', 2100, 2000),
                                                  AntibodyMatchTypes.SPLIT)],
                                   is_type_a=False)
        # first matching antibody with mfi > cutoff, second with mfi < cutoff  # SPLIT_1
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2100, 2000),
                                                  AntibodyMatchTypes.SPLIT)],
                                   is_type_a=False)

        # first matching antibody with mfi > cutoff, second with mfi < cutoff  # SPLIT_2
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A23', 2100, 2000),
                                    create_antibody('A*23:04', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A23', 2100, 2000),
                                                  AntibodyMatchTypes.SPLIT)],
                                   is_type_a=False)

        # first matching antibody with mfi > cutoff, second with mfi < cutoff  # HIGH_RES_WITH_SPLIT_1
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 2100, 2000),
                                    create_antibody('A*23:04', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:01', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES_WITH_SPLIT)],
                                   is_type_a=True)

        # first matching antibody with mfi > cutoff, second with mfi < cutoff  # HIGH_RES_WITH_SPLIT_2
        self._assert_matches_equal('A*24:02',
                                   [create_antibody('A*24:37', 2100, 2000),
                                    create_antibody('A*24:85', 1900, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*24:37', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES_WITH_SPLIT)],
                                   is_type_a=True)

        # broad matches:

        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # BROAD_1
        self._assert_matches_equal('A9',
                                   [create_antibody('A9', 1900, 2000),
                                    create_antibody('A9', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A9', 2000, 2000), AntibodyMatchTypes.BROAD)],
                                   is_type_a=False)

        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # BROAD_2
        self._assert_matches_equal('A*23:01',
                                   [create_antibody('A9', 1900, 2000),
                                    create_antibody('A9', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A9', 2000, 2000), AntibodyMatchTypes.BROAD)],
                                   is_type_a=False)

        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # BROAD_2
        self._assert_matches_equal('A23',
                                   [create_antibody('A9', 1900, 2000),
                                    create_antibody('A9', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A9', 2000, 2000), AntibodyMatchTypes.BROAD)],
                                   is_type_a=False)

        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # BROAD_2
        self._assert_matches_equal('A9',
                                   [create_antibody('A9', 1900, 2000),
                                    create_antibody('A9', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A9', 2000, 2000), AntibodyMatchTypes.BROAD)],
                                   is_type_a=False)

        # first matching antibody with mfi < cutoff, second with mfi > cutoff  # HIGH_RES_WITH_BROAD_1
        self._assert_matches_equal('A9',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('A*23:04', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES_WITH_BROAD)],
                                   is_type_a=True)

        # first matching antibody with mfi < cutoff, second with mfi < cutoff
        # type A
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 1800, 2000)], True,
                                   [],
                                   is_type_a=True)
        # type B
        self._assert_matches_equal('A23',
                                   [create_antibody('A*23:01', 1900, 2000),
                                    create_antibody('A*23:04', 1800, 2000)], True,
                                   [],
                                   is_type_a=False)

        # undecidable and none typization with HIGH_RES_1
        self._assert_matches_equal('DPB1*858:01',
                                   [create_antibody('DPB1*858:01', 2100, 2000),
                                    create_antibody('DPB1*1016:01', 2100, 2000),
                                    create_antibody('DQB1*03:10', 2100, 2000)], True,
                                   [AntibodyMatch(create_antibody_parsed('DPB1*858:01', 2100, 2000),
                                                  AntibodyMatchTypes.HIGH_RES),
                                    AntibodyMatch(create_antibody_parsed('DPB1*1016:01', 2100, 2000),
                                                  AntibodyMatchTypes.NONE),
                                    AntibodyMatch(create_antibody_parsed('DQB1*03:10', 2100, 2000),
                                                  AntibodyMatchTypes.UNDECIDABLE)],
                                   is_type_a=False)

    def test_crossmatch_level(self):
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertFalse(AntibodyMatchTypes.NONE.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.HIGH_RES.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertTrue(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertTrue(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.SPLIT.is_positive_for_level(HLACrossmatchLevel.NONE))

        self.assertTrue(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.SPLIT_AND_BROAD))
        self.assertTrue(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.BROAD))
        self.assertTrue(AntibodyMatchTypes.BROAD.is_positive_for_level(HLACrossmatchLevel.NONE))

    def test_virtual_crossmatch_if_all_antibodies_positive_in_high_res(self):
        high_res_antibodies_all_positive = [create_antibody('A*24:02', 2100, 2000),
                                            create_antibody('A*23:01', 2100, 2000),
                                            create_antibody('A*23:04', 2100, 2000)]
        high_res_antibodies_not_all_positive = [create_antibody('A*24:02', 1900, 2000),
                                                create_antibody('A*23:01', 2100, 2000),
                                                create_antibody('A*23:04', 2100, 2000)]

        self._assert_negative_crossmatch('A9', high_res_antibodies_not_all_positive, True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.BROAD)

        self._assert_positive_crossmatch('A9', high_res_antibodies_all_positive, True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.BROAD)

        self._assert_positive_crossmatch('A9', high_res_antibodies_not_all_positive, True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.NONE)

        self._assert_positive_crossmatch('A9', high_res_antibodies_all_positive, True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.NONE)

        self._assert_negative_crossmatch('A23',
                                         [create_antibody('A*23:01', 1900, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.SPLIT_AND_BROAD)

        self._assert_positive_crossmatch('A23',
                                         [create_antibody('A*23:01', 2100, 2000),
                                          create_antibody('A*23:04', 2100, 2000)], True,
                                         crossmatch_logic=do_crossmatch_in_type_a,
                                         crossmatch_level=HLACrossmatchLevel.SPLIT_AND_BROAD)

    def test_crossmatch_for_antibodies_with_two_codes(self):
        hla_antibodies = create_antibodies(hla_antibodies_list=[])
        hla_antibodies.hla_antibodies_per_groups[4].hla_antibody_list.append(
            create_antibody_parsed('DPA1*01:03', 2100, 2000, 'DPB1*18:01')
        )

        self.assertFalse(is_positive_hla_crossmatch(create_hla_typing(hla_types_list=['DPA1*01:03']),
                                                    hla_antibodies,
                                                    use_high_resolution=True,
                                                    crossmatch_logic=do_crossmatch_in_type_a))

        self.assertTrue(is_positive_hla_crossmatch(create_hla_typing(hla_types_list=['DPA1*01:03', 'DPB1*18:01']),
                                                   hla_antibodies,
                                                   use_high_resolution=True,
                                                   crossmatch_logic=do_crossmatch_in_type_a))

        hla_antibodies = create_antibodies(hla_antibodies_list=[])
        hla_antibodies.hla_antibodies_per_groups[4].hla_antibody_list.append(
            create_antibody_parsed('DPA1*02:01', 2100, 2000, 'DPB1*02:01'))

        self.assertTrue(is_positive_hla_crossmatch(create_hla_typing(hla_types_list=['DPA1*02:02', 'DPB1*02:02']),
                                                   hla_antibodies,
                                                   use_high_resolution=True,
                                                   crossmatch_logic=do_crossmatch_in_type_a))

        self.assertFalse(is_positive_hla_crossmatch(create_hla_typing(hla_types_list=['DPB2']),
                                                    hla_antibodies,
                                                    use_high_resolution=True,
                                                    crossmatch_logic=do_crossmatch_in_type_a))

        self.assertTrue(is_positive_hla_crossmatch(create_hla_typing(hla_types_list=['DPA1*02:02', 'DPB2']),
                                                   hla_antibodies,
                                                   use_high_resolution=True,
                                                   crossmatch_logic=do_crossmatch_in_type_a))

        antibodies = create_antibodies(hla_antibodies_list=[])
        antibodies.hla_antibodies_per_groups[4].hla_antibody_list.append(
            create_antibody_parsed('DPB1*18:02', 1900, 2000))
        antibodies.hla_antibodies_per_groups[4].hla_antibody_list.append(
            create_antibody_parsed('DPA1*01:02', 1900, 2000))
        antibodies.hla_antibodies_per_groups[4].hla_antibody_list.append(
            create_antibody_parsed('DPA1*01:03', 2100, 2000, 'DPB1*18:01'))
        crossmatch_result = do_crossmatch_in_type_a(
            create_hla_typing(hla_types_list=['DPA1', 'DP18']),
            antibodies,
            use_high_resolution=True,
        )

        self.assertEqual(crossmatch_result[4].antibody_matches[0].match_type, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT)
