
PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS = {
    # Based on email communication with Matej Roder from 31.12.2020. This conversion does not fit the logic of
    # taking assumed serology code. This is because the primary source is not 100% correct. DQB1*03:19 is structurally
    # closest to DQB1*03:01, which corresponds to split DQ7, not DQ3
    'DQB1*03:19': 'DQ7',
}

PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES = {
    'C*04:03': ['CW4', 'CW6']
}

MULTIPLE_SERO_CODES_LIST = list({code for code_list in PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.values()
                                 for code in code_list})
