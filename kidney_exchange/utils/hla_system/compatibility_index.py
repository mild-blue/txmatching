from kidney_exchange.patients.patient_parameters import PatientParameters
from kidney_exchange.utils.hla_system.get_genotype import get_antigen_genotype

compatibility_gene_codes = ["A", "B", "DR"]
# TODO: ask what exact antigens should I count in the matches - for example what about DR52, DR53
_compatibility_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
_A_matches_count = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]
_B_matches_count = [0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2]
_DR_matches_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2]

_ABDR_matches_count_to_compatibility_index = {
    (A, B, DR): CI for A, B, DR, CI in
    zip(_A_matches_count, _B_matches_count, _DR_matches_count, _compatibility_index)
}


def compatibility_index(patient_parameters_donor: PatientParameters,
                        patient_parameters_recipient: PatientParameters) -> float:
    match_counts = {code: 0 for code in compatibility_gene_codes}

    for gene_code in compatibility_gene_codes:
        donor_genotype = get_antigen_genotype(patient_parameters_donor.hla_antigens_low_resolution, gene_code)
        recipient_genotype = get_antigen_genotype(patient_parameters_recipient.hla_antigens_low_resolution, gene_code)
        common_allele_codes = set(donor_genotype.keys()).intersection(set(recipient_genotype.keys()))

        match_count = 0
        for allele_code in common_allele_codes:
            match_count += min(donor_genotype[allele_code], recipient_genotype[allele_code])

        match_counts[gene_code] = match_count

    match_counts_tuple = tuple([match_counts[gene_code] for gene_code in compatibility_gene_codes])
    return _ABDR_matches_count_to_compatibility_index[match_counts_tuple]
