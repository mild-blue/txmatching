import logging
import unittest

from txmatching.patients.patient_parameters import HLAAntibodies, HLAAntigens
from txmatching.utils.hla_system.hla_crossmatch import is_positive_hla_crossmatch, is_positive_hla_crossmatch_obsolete
from txmatching.utils.hla_system.hla_table import split_to_broad

logger = logging.getLogger(__name__)


class TestCrossmatch(unittest.TestCase):

    def test_crossmatch(self):
        self.assertEqual('A9', split_to_broad['A23'])
        self.assertEqual('A9', split_to_broad['A24'])
        self.assertTrue(is_positive_hla_crossmatch(HLAAntigens(codes=['A23']),
                                                   HLAAntibodies(codes=['A24']),
                                                   False))
        self.assertTrue(is_positive_hla_crossmatch(HLAAntigens(codes=['A9']),
                                                   HLAAntibodies(codes=['A9']),
                                                   False))
        self.assertTrue(is_positive_hla_crossmatch(HLAAntigens(codes=['A9']),
                                                   HLAAntibodies(codes=['A23']),
                                                   False))
        self.assertFalse(is_positive_hla_crossmatch(HLAAntigens(codes=['A23']),
                                                    HLAAntibodies(codes=['A24']),
                                                    True))
        self.assertTrue(is_positive_hla_crossmatch(HLAAntigens(codes=['A9']),
                                                   HLAAntibodies(codes=['A9']),
                                                   True))
        self.assertTrue(is_positive_hla_crossmatch(HLAAntigens(codes=['A9']),
                                                   HLAAntibodies(codes=['A23']),
                                                   True))

        self.assertFalse(is_positive_hla_crossmatch_obsolete(HLAAntigens(codes=['A23']),
                                                             HLAAntibodies(codes=['A24'])))
        self.assertTrue(is_positive_hla_crossmatch_obsolete(HLAAntigens(codes=['A9']),
                                                            HLAAntibodies(codes=['A9'])))
        self.assertIsNone(is_positive_hla_crossmatch_obsolete(HLAAntigens(codes=['A9']),
                                                              HLAAntibodies(codes=['A23'])))
