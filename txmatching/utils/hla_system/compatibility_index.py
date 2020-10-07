from txmatching.patients.patient_parameters import HLATyping
from txmatching.utils.enums import HLA_TYPING_BONUS_PER_GENE_CODE
from txmatching.utils.hla_system.get_genotype import get_antigen_genotype


# Traditionally one can calculate index of incompatibility (IK) - the higher IK the higher incompatibility.
# You calculate it by calculating the number of differences in A, B, DR alleles and look up the corresponding
# column in the incompatibility index table.
# For our purposes, we will use the index of compatibility, which is the inverse of index of incompatibility
# -- see function compatibility_index -- and is calculated as the number of matches in A, B, DR alleles.
# For each matching allele a certain bonus is added to compatibility index depending on the allele type.


def compatibility_index(donor_hla_typing: HLATyping,
                        recipient_hla_typing: HLATyping) -> float:
    """
    The "compatibility index" is terminus technicus defined by immunologist:
    we calculate number of matches per Compatibility HLA indices and add bonus according
     to number of matches and the HLA code.
    This function thus should not be modified unless after consulting with immunologists.
    """
    hla_compatibility_index = 0.0
    for gene_code, ci_bonus in HLA_TYPING_BONUS_PER_GENE_CODE.items():
        donor_genotype = get_antigen_genotype(donor_hla_typing.compatibility_broad_resolution_codes, gene_code)
        recipient_genotype = get_antigen_genotype(recipient_hla_typing.compatibility_broad_resolution_codes, gene_code)
        common_allele_codes = set(donor_genotype.keys()).intersection(set(recipient_genotype.keys()))

        match_count = 0
        for allele_code in common_allele_codes:
            match_count += min(donor_genotype[allele_code], recipient_genotype[allele_code])

        hla_compatibility_index += match_count * ci_bonus

    return hla_compatibility_index
