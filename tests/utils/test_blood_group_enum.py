import unittest

from txmatching.utils.blood_groups import BloodGroup


class TestAcceptableBloodGroupParsing(unittest.TestCase):
    def test_blood_group_parsing(self):
        self.assertEqual(BloodGroup.A, BloodGroup('A'))
        self.assertEqual(BloodGroup.ZERO, BloodGroup(0))
        self.assertEqual('0', str(BloodGroup(0)))
