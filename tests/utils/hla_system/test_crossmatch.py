import logging
import unittest

from txmatching.patients.patient_parameters import HLAAntibodies, HLATyping
from txmatching.utils.hla_system.hla_crossmatch import \
    is_positive_hla_crossmatch
from txmatching.utils.hla_system.hla_table import SPLIT_TO_BROAD

logger = logging.getLogger(__name__)


class TestCrossmatch(unittest.TestCase):

    def test_crossmatch(self):
        self.assertEqual('A9', SPLIT_TO_BROAD['A23'])
        self.assertEqual('A9', SPLIT_TO_BROAD['A24'])
        self.assertTrue(is_positive_hla_crossmatch(HLATyping(codes=['A23']),
                                                   HLAAntibodies(codes=['A24']),
                                                   False))
        self.assertTrue(is_positive_hla_crossmatch(HLATyping(codes=['A9']),
                                                   HLAAntibodies(codes=['A9']),
                                                   False))
        self.assertTrue(is_positive_hla_crossmatch(HLATyping(codes=['A9']),
                                                   HLAAntibodies(codes=['A23']),
                                                   False))
        self.assertFalse(is_positive_hla_crossmatch(HLATyping(codes=['A23']),
                                                    HLAAntibodies(codes=['A24']),
                                                    True))
        self.assertTrue(is_positive_hla_crossmatch(HLATyping(codes=['A9']),
                                                   HLAAntibodies(codes=['A9']),
                                                   True))
        self.assertTrue(is_positive_hla_crossmatch(HLATyping(codes=['A9']),
                                                   HLAAntibodies(codes=['A23']),
                                                   True))
