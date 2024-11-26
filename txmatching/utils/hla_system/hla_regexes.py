import re
from typing import Optional

HIGH_RES_REGEX_STRING = r'^([A-Z]+\d?\*\d{2,4}(:\d{2,4}))(:\d{2,4})*'
HIGH_RES_REGEX = re.compile(HIGH_RES_REGEX_STRING+r'$')  # with high res subunit
HIGH_RES_REGEX_ENDING_WITH_LETTER = re.compile(HIGH_RES_REGEX_STRING+r'([A-Z])$')
HIGH_RES_WITH_SUBUNITS_REGEX = re.compile(r'(DP|DQ)\d?\[(\d{2}:\d{2}),(\d{2}:\d{2})]')
LOW_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}[A-Z]?$')
SPLIT_RES_REGEX = re.compile(r'^[A-Z]+\d+$')

CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX = re.compile(r'C(\d+)')
B_SEROLOGICAL_CODE_WITH_W_REGEX = re.compile(r'BW(\d+)')
DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX = re.compile(r'(D[QP])([AB])(\d+)')


def try_get_hla_high_res(hla_raw_code: str, regex=HIGH_RES_REGEX) -> Optional[str]:
    high_res_match = regex.search(hla_raw_code)
    if high_res_match:
        high_res = high_res_match.group(1)
        return high_res
    return None
