import unittest

from txmatching.configuration.app_configuration.application_configuration import \
    ApplicationEnvironment


class TestEnums(unittest.TestCase):
    def test_enum_creation(self):
        self.assertEqual(ApplicationEnvironment.PRODUCTION, ApplicationEnvironment('PRODUCTION'))
        with self.assertRaises(ValueError):
            ApplicationEnvironment('TEST')
