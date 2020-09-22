import logging
import unittest

from tests.patients.test_patient_parameters import (donor_parameters_Joe,
                                                    recipient_parameters_Jack)
from txmatching.utils.hla_system.get_genotype import get_antigen_genotype
from txmatching.utils.hla_system.hla_table import CompatibilityGeneCode

logger = logging.getLogger(__name__)


class TestGetGenotype(unittest.TestCase):
    def setUp(self):
        self._patient_params_genotypes = [(donor_parameters_Joe, {'A': {'A10': 1, 'A11': 1},
                                                                  'B': {'B16': 1, 'B15': 1},
                                                                  'DR': {'DR4': 1, 'DR5': 1}}),
                                          (recipient_parameters_Jack, {'A': {'A1': 1, 'A19': 1},
                                                                       'B': {'B15': 1, 'B14': 1},
                                                                       'DR': {'DR4': 1, 'DR5': 1}})]

    def test_get_genotype(self):
        logger.info('Testing get_genotype')
        for patient_params, genotypes in self._patient_params_genotypes:
            logger.info(f'Original HLA typing: {str(patient_params.hla_typing)}')
            logger.info(f'Broad HLA typing: {str(patient_params.hla_typing.hla_typing_broad_resolution)}')
            for gene_code in CompatibilityGeneCode:
                calculated_genotype = get_antigen_genotype(patient_params.hla_typing.hla_typing_broad_resolution,
                                                           gene_code)
                expected_genotype = genotypes[gene_code]
                self.assertEqual(calculated_genotype, expected_genotype)
                logger.info(f'{gene_code} genotype: {str(calculated_genotype)}')
        logger.info('    -- done\n')
