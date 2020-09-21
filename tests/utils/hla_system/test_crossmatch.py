import logging
import unittest

from txmatching.patients.patient_parameters import HLAAntibodies, HLAAntigens
from txmatching.utils.hla_system.hla_crossmatch import is_positive_hla_crossmatch, is_positive_hla_crossmatch_obsolete
from txmatching.utils.hla_system.hla_table import broad_for_split

logger = logging.getLogger(__name__)


class TestCrossmatch(unittest.TestCase):

    def test_crossmatch(self):
        broad = ['A11', 'A10', 'B16', 'B15', 'DR4', 'DR5', 'DR52', 'DR53',
                 'DQ3', 'DQ3', 'DP2', 'DP10', 'Cw3', 'Cw12']
        self.assertEqual('A9', broad_for_split['A23'])
        self.assertEqual('A9', broad_for_split['A24'])
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
