from typing import Dict, List

from txmatching.utils.enums import HLATypes
from txmatching.utils.hla_system.hla_table import COMPATIBILITY_BROAD_CODES


def get_antigen_genotype(compatibility_broad_codes: List[str], gene_code: HLATypes) -> Dict[str, int]:
    """
    Returns the genotype for specific antigen
    for example for A it can be (A9, A10), or (A9, A9) etc. (In case we see only one genotype we assume it means that
    patient has this genotype twice in fact
    :param compatibility_broad_codes: compatibility broad codes of patient antigen alleles e.g. [A9, B19, DR5, A10 ...]
    :param gene_code: gene code of the antigen of interest, e.g. A or B or DR
    :return: e.g. {"A9": 1, "A10": 1} or {"A9": 2}
    """
    assert set(compatibility_broad_codes).issubset(COMPATIBILITY_BROAD_CODES), \
        'To get antigen genotypes only compatibility broad codes shall be provided'
    compatibility_broad_codes = {code for code in compatibility_broad_codes if code.startswith(gene_code)}
    if len(compatibility_broad_codes) == 1:
        return {compatibility_broad_codes.pop(): 2}
    elif len(compatibility_broad_codes) == 2:
        return {allele_code: 1 for allele_code in compatibility_broad_codes}
    else:
        raise AssertionError(f'Invalid list of alleles for gene {gene_code} - there have to be 1 or 2 per gene.'
                             f'\nList of patient_alleles: {compatibility_broad_codes}')
