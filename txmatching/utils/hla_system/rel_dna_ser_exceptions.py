from txmatching.utils.hla_system.hla_regexes import try_convert_ultra_high_res
from txmatching.utils.hla_system.hla_table import HIGH_RES_TO_SPLIT_OR_BROAD
from txmatching.utils.hla_system.rel_dna_ser_parsing import (
    PATH_TO_REL_DNA_SER, parse_rel_dna_ser_expert_exceptions)


def _get_multiple_hla_codes_due_to_expert_exceptions():
    """
    If expert exceptions are given for an already parsed HLA in high resolution,
    then there is a multiple split value for this HLA.
    """
    high_res_multiple_split = {}
    for key, split in parse_rel_dna_ser_expert_exceptions(PATH_TO_REL_DNA_SER)\
            .split.dropna().to_dict().items():
        key = try_convert_ultra_high_res(key)
        if key is not None and key in HIGH_RES_TO_SPLIT_OR_BROAD \
                and HIGH_RES_TO_SPLIT_OR_BROAD[key] != split:
            high_res_multiple_split[key] = {HIGH_RES_TO_SPLIT_OR_BROAD[key], split}

    return high_res_multiple_split


PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS = {
    # Based on email communication with Matej Roder from 19.10.2020
    'B*82:02': 'B82',
    'DRB1*09:02': 'DR9',
    # Based on email communication with Matej Roder from 31.12.2020
    'DQB1*03:19': 'DQ7',  # DQB1*03:19 is structurally closest to DQB1*03:01, which corresponds
                          # to split DQ7. Although it is possible that some antibodies
                          # may not be against this allele.
    'DRB1*07:07': 'DR7',
    # Based on email communication with Matej Roder from 12.7.2021
    'C*07:18': 'CW7',
    # Based on email communication with Matej Roder from 11.1.2022
    'A*26:12': 'A26',
    # Based on email communication with Matej Roder from 8.6.2022
    'A*32:03': 'A32',
    # Based on slack with Matej Roder from 17.10.2022
    'A*24:95': 'A24',
    # Based on data from Italy from 26.10.2022
    'DRB1*10:03': 'DR10'
}

PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES = {
    'C*04:03': ['CW4', 'CW6']
} | _get_multiple_hla_codes_due_to_expert_exceptions()

MULTIPLE_SERO_CODES_LIST = list({code for code_list in PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.values()
                                 for code in code_list})
