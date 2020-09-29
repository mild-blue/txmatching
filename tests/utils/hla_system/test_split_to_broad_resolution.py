import logging
import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe, recipient_parameters_Jack)
from txmatching.utils.hla_system.hla_transformations import split_to_broad

logger = logging.getLogger(__name__)


class TestSplitToBroadResolution(unittest.TestCase):
    def setUp(self):
        self._original_split_and_expected_broad_res = [(donor_parameters_Joe.hla_typing,
                                                        {'A11', 'A10', 'B16', 'B15', 'DR4', 'DR5', 'DR52', 'DR53',
                                                         'DQ3', 'DQ3', 'CW3'}
                                                        ),
                                                       (recipient_parameters_Jack.hla_typing,
                                                        {'A1', 'A19', 'B14', 'B15', 'B15', 'B15', 'B14', 'B14', 'B15',
                                                         'B15', 'B15', 'DR4', 'DR5'}
                                                        )]

    def test_hla_split_to_broad_res(self):
        logger.info('Testing hla_split_to_broad_res')
        for split_res_codes, expected_broad_res_codes in self._original_split_and_expected_broad_res:
            calculated_broad_res_codes = {split_to_broad(code) for code in split_res_codes.codes if
                                          split_to_broad(code)}
            self.assertSetEqual(calculated_broad_res_codes, expected_broad_res_codes)
        logger.info('    -- done\n')
