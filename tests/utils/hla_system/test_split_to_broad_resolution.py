import logging
import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack)
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.utils.hla_system.hla_transformations.utils import (
    broad_to_split, split_to_broad)

logger = logging.getLogger(__name__)


class TestSplitToBroadResolution(DbTests):
    def setUp(self):
        super().setUp()
        self._original_split_and_expected_broad_res = [(donor_parameters_Joe.hla_typing,
                                                        {'A9', 'A10', 'B16', 'B15', 'DR4', 'DR5', 'DR52', 'DR53',
                                                         'DQ3', 'DQ3', 'CW3', 'DP2', 'DP10', 'CW12'}
                                                        ),
                                                       (recipient_parameters_Jack.hla_typing,
                                                        {'A9', 'A19', 'B14', 'B15', 'B15', 'B15', 'B14', 'B14', 'B15',
                                                         'B15', 'B15', 'DR4', 'DR5'}
                                                        )]

    def test_hla_split_to_broad_res(self):
        for split_res_codes, expected_broad_res_codes in self._original_split_and_expected_broad_res:
            calculated_broad_res_codes = {
                split_to_broad(hla.code.split if hla.code.split is not None else hla.code.broad)
                for group_codes in split_res_codes.hla_per_groups
                for hla in group_codes.hla_types
            }
            self.assertSetEqual(expected_broad_res_codes, calculated_broad_res_codes)

    def test_hla_broad_to_split_res(self):
        self.assertSetEqual({'A23', 'A24'}, set(broad_to_split('A9')))
        self.assertSetEqual({'A23'}, set(broad_to_split('A23')))
        self.assertSetEqual({'DQ7', 'DQ8', 'DQ9'}, set(broad_to_split('DQ3')))
        self.assertSetEqual({'CW12'}, set(broad_to_split('CW12')))
