
PARSE_HIGH_RES_HLA_CODE_EXCEPTIONS = {
    # Based on email communication with Matej Roder from 31.12.2020. This conversion does not fit the logic of
    # taking assumed serology code. This is because the primary source is not 100% correct. DQB1*03:19 is structurally
    # closest to DQB1*03:01, which corresponds to split DQ7, not DQ3
    'DQB1*03:19': 'DQ7',

    # Codes that comply with assumed serology, but were confirmed by immunologist
    # Based on email communication with Matej Roder from 19.10.2020
    'B*82:02': 'B82',
    'DRB1*09:02': 'DR9',
    # Based on email communication with Matej Roder from 31.12.2020
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
}

MULTIPLE_SERO_CODES_LIST = list({code for code_list in PARSE_HLA_CODE_EXCEPTIONS_MULTIPLE_SEROLOGICAL_CODES.values()
                                 for code in code_list})
