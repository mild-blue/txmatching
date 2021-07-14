import re
from typing import Optional

HIGH_RES_REGEX_STRING = r'^([A-Z]+\d?\*\d{2,4}(:\d{2,3}))(:\d{2,3})*'
HIGH_RES_REGEX = re.compile(HIGH_RES_REGEX_STRING+r'$')  # with high res subunit
HIGH_RES_REGEX_ENDING_WITH_LETTER = re.compile(HIGH_RES_REGEX_STRING+r'([A-Z])$')
HIGH_RES_WITH_SUBUNITS_REGEX = re.compile(r'(DP|DQ)\d?\[(\d{2}:\d{2}),(\d{2}:\d{2})]')
LOW_RES_REGEX = re.compile(r'^[A-Z]+\d?\*\d{2,4}[A-Z]?$')
SPLIT_RES_REGEX = re.compile(r'^[A-Z]+\d+$')

CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX = re.compile(r'C(\d+)')
B_SEROLOGICAL_CODE_WITH_W_REGEX = re.compile(r'BW(\d+)')
DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX = re.compile(r'(D[QP])([AB])(\d+)')


def try_convert_ultra_high_res(high_res_or_ultra_high_res: str) -> Optional[str]:
    match = HIGH_RES_REGEX.search(high_res_or_ultra_high_res)
    if match:
        high_res = match.group(1)
        return high_res
    else:
        return None


def try_convert_high_res_with_letter(high_res_or_ultra_high_res: str) -> Optional[str]:
    match = HIGH_RES_REGEX_ENDING_WITH_LETTER.search(high_res_or_ultra_high_res)
    if match:
        high_res = match.group()
        return high_res
    else:
        return ''
