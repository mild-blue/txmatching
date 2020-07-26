import pandas as pd

from kidney_exchange.patients.patient_parameters import PatientParameters
from kidney_exchange.utils.hla_system.get_genotype import get_antigen_genotype

compatibility_gene_codes = ["A", "B", "DR"]

# The following table is the of index of incompatibility - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
IK_table = pd.DataFrame({"A": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
                         "B": [0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2],
                         "DR": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                         "IK": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                                24, 25, 26]})
IK_table.set_index(keys=compatibility_gene_codes, inplace=True, verify_integrity=True)


def compatibility_index(patient_parameters_donor: PatientParameters,
                        patient_parameters_recipient: PatientParameters) -> float:
    """
    The "compatibility index" is terminus technicus defined by the IK_table dataframe.
    This function thus should not be modified unless after consulting with immunologists.
    """
    match_counts = {code: 0 for code in compatibility_gene_codes}

    for gene_code in compatibility_gene_codes:
        donor_genotype = get_antigen_genotype(patient_parameters_donor.hla_antigens_broad_resolution, gene_code)
        recipient_genotype = get_antigen_genotype(patient_parameters_recipient.hla_antigens_broad_resolution, gene_code)
        common_allele_codes = set(donor_genotype.keys()).intersection(set(recipient_genotype.keys()))

        match_count = 0
        for allele_code in common_allele_codes:
            match_count += min(donor_genotype[allele_code], recipient_genotype[allele_code])

        match_counts[gene_code] = match_count

    match_counts_tuple = tuple([match_counts[gene_code] for gene_code in compatibility_gene_codes])
    hal_compatibility_index = IK_table.loc[match_counts_tuple, "IK"]

    return hal_compatibility_index
