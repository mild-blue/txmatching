from typing import List, Dict


def get_antigen_genotype(patient_allele_codes: List[str], gene_code: str = "A") -> Dict[str, int]:
    """
    Returns the genotype for specific antigen
    for example for A it can be (A9, A10), or (A9, A9) etc.
    :param patient_allele_codes: low resolution codes of patient antigen alleles e.g. [A9, B19, DR5, A10 ...]
    :param gene_code: gene code of the antigen of interest, e.g. A or B or DR
    :return: e.g. {"A9": 1, "A10": 1} or {"A9": 2}
    """
    # In the following: list(set()) is for case A30, A31, A32 > A19, A19, A19
    patient_allele_codes = list(set([code for code in patient_allele_codes if code.startswith(gene_code)]))
    if len(patient_allele_codes) == 0:
        return dict()  # TODO handle as error?
    elif len(patient_allele_codes) == 1:
        return {patient_allele_codes[0]: 2}
    elif len(patient_allele_codes) == 2:
        return {allele_code: 1 for allele_code in patient_allele_codes}
    else:
        raise AssertionError(f"Invalid list of alleles for gene {gene_code} - there have to be exactly 2 per one gene."
                             f"\nList of patient_alleles: {patient_allele_codes}")
