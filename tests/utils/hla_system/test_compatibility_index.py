import unittest

from kidney_exchange.utils.hla_system.compatibility_index import compatibility_index
from tests.patients.test_patient_parameters import donor_parameters_Joe, recipient_parameters_Jack


class TestCompatibilityIndex(unittest.TestCase):
    def setUp(self):
        self._donor_params = donor_parameters_Joe
        self._recipient_params = recipient_parameters_Jack

    def test_compatibility_index(self):
        compatibility_index(self._donor_params, self._recipient_params)
        # TODO: Finish - prerequisity is TODO in high_resolution_to_low_resolution
        print(compatibility_index())
