import logging
import unittest

from txmatching.utils.hla_system.compatibility_index import compatibility_index
from tests.patients.test_patient_parameters import donor_parameters_Joe, recipient_parameters_Jack

logger = logging.getLogger(__name__)


class TestCompatibilityIndex(unittest.TestCase):
    def setUp(self):
        self._donor_recipient_index = [(donor_parameters_Joe, recipient_parameters_Jack, 21.0)]

    def test_compatibility_index(self):
        logger.info("Testing compatibility index")
        for donor_params, recipient_params, expected_compatibility_index in self._donor_recipient_index:
            calculated_compatibility_index = compatibility_index(donor_params.hla_typing,
                                                                 recipient_params.hla_typing)
            self.assertEqual(calculated_compatibility_index, expected_compatibility_index)
        logger.info("    -- done\n")
