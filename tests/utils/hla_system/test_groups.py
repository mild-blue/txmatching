from txmatching.utils.hla_system.hla_preparation_utils import create_hla_type
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.hla_functions import split_hla_types_to_groups
from txmatching.patients.hla_model import HLAType
from txmatching.utils.enums import HLAGroup


class TestCodeParser(DbTests):

    def _assert_split_to_groups(self, hla_type: HLAType, expected_group: HLAGroup):
        hla_per_groups = split_hla_types_to_groups([hla_type])[1]

        self.assertEqual(8, len(hla_per_groups))
        group_found = False
        for group in hla_per_groups:
            if group.hla_group == expected_group:
                self.assertCountEqual([hla_type], group.hla_types)
                group_found = True
            else:
                self.assertCountEqual([], group.hla_types, f'The group should be empty: {group}')

        self.assertTrue(group_found)

    def test_assert(self):
        with self.assertRaises(AssertionError):
            self._assert_split_to_groups(create_hla_type('A23'), HLAGroup.B)

        with self.assertRaises(AssertionError):
            self._assert_split_to_groups(create_hla_type('A23'), HLAGroup.CW)

    def test_split_codes(self):
        self._assert_split_to_groups(create_hla_type('A23'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('B7'), HLAGroup.B)
        self._assert_split_to_groups(create_hla_type('DR11'), HLAGroup.DRB1)

    def test_high_res_codes(self):
        self._assert_split_to_groups(create_hla_type('A*01:01:01:01'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('A*01:01'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('A*01'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('B*15:10'), HLAGroup.B)
        self._assert_split_to_groups(create_hla_type('DQA1*01:03'), HLAGroup.DQ)
        self._assert_split_to_groups(create_hla_type('DRB4*01:01'), HLAGroup.OTHER_DR)
        self._assert_split_to_groups(create_hla_type('C*01:02'), HLAGroup.CW)

        # high res with letter
        self._assert_split_to_groups(create_hla_type('A*02:284N'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('A*11:21N'), HLAGroup.A)
        self._assert_split_to_groups(create_hla_type('C*01:37N'), HLAGroup.CW)
        self._assert_split_to_groups(create_hla_type('DRB1*01:33N'), HLAGroup.DRB1)
        self._assert_split_to_groups(create_hla_type('DRB1*04:280N'), HLAGroup.DRB1)
        self._assert_split_to_groups(create_hla_type('DPA1*01:29N'), HLAGroup.DP)
        self._assert_split_to_groups(create_hla_type('DQA1*01:15N'), HLAGroup.DQ)
        self._assert_split_to_groups(create_hla_type('DRB3*01:26N'), HLAGroup.OTHER_DR)
        self._assert_split_to_groups(create_hla_type('DPB1*120:01N'), HLAGroup.DP)
