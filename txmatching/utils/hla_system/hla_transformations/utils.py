import logging
import re
from typing import List, Optional

from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_regexes import (
    B_SEROLOGICAL_CODE_WITH_W_REGEX, CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX,
    DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX)
from txmatching.utils.hla_system.hla_table import (ALL_SPLIT_BROAD_CODES,
                                                   BROAD_CODES,
                                                   IRRELEVANT_CODES,
                                                   SPLIT_CODES, SPLIT_TO_BROAD)
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result import \
    HlaCodeProcessingResult
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail

logger = logging.getLogger(__name__)


def broad_to_split(hla_code: str) -> List[str]:
    if hla_code not in ALL_SPLIT_BROAD_CODES:
        logger.warning(f'Unexpected hla_code: {hla_code}')
        return [hla_code]
    splits = [split for split, broad in SPLIT_TO_BROAD.items() if broad == hla_code]
    return splits if splits else [hla_code]


def split_to_broad(hla_code: str) -> str:
    return SPLIT_TO_BROAD.get(hla_code, hla_code)


def _cleanup_split_or_broad_code(serological_hla_code: str) -> str:
    c_match = re.match(CW_SEROLOGICAL_CODE_WITHOUT_W_REGEX, serological_hla_code)
    if c_match:
        serological_hla_code = f'CW{int(c_match.group(1))}'

    b_match = re.match(B_SEROLOGICAL_CODE_WITH_W_REGEX, serological_hla_code)
    if b_match:
        # doesn't actually do anything atm, but Bw is a special kind of antigen so we want to keep the branch here
        serological_hla_code = f'BW{int(b_match.group(1))}'

    dpqb_match = re.match(DQ_DP_SEROLOGICAL_CODE_WITH_AB_REGEX, serological_hla_code)
    if dpqb_match:
        subtype_str = 'A' if dpqb_match.group(2) == 'A' else ''
        serological_hla_code = f'{dpqb_match.group(1)}{subtype_str}{int(dpqb_match.group(3))}'
    return serological_hla_code


def process_parsing_result(high_res: Optional[str],
                           split_or_broad_raw: Optional[str],
                           detail: Optional[ParsingIssueDetail] = None) -> HlaCodeProcessingResult:
    if split_or_broad_raw is None:
        assert detail is not None
        return HlaCodeProcessingResult(
            HLACode(
                high_res=high_res,
                split=None,
                broad=None
            ),
            detail
        )
    split_or_broad_raw = _cleanup_split_or_broad_code(split_or_broad_raw)
    if split_or_broad_raw in SPLIT_CODES:
        # Raw code was high res or split
        return HlaCodeProcessingResult(
            HLACode(
                high_res=high_res,
                split=split_or_broad_raw,
                broad=split_to_broad(split_or_broad_raw)
            ),
            detail if detail is not None else ParsingIssueDetail.SUCCESSFULLY_PARSED
        )
    if split_or_broad_raw in BROAD_CODES:
        if high_res is not None:
            detail = ParsingIssueDetail.HIGH_RES_WITHOUT_SPLIT
        return HlaCodeProcessingResult(
            HLACode(
                high_res=high_res,
                split=None,
                broad=split_to_broad(split_or_broad_raw)
            ),
            detail if detail is not None else ParsingIssueDetail.SUCCESSFULLY_PARSED
        )
    if split_or_broad_raw in IRRELEVANT_CODES:
        return HlaCodeProcessingResult(
            HLACode(
                high_res=high_res,
                split=split_or_broad_raw,
                broad=split_or_broad_raw
            ), detail if detail else ParsingIssueDetail.IRRELEVANT_CODE)
    return HlaCodeProcessingResult(
        HLACode(
            high_res=high_res,
            split=split_or_broad_raw,
            broad=split_or_broad_raw
        ), detail if detail else ParsingIssueDetail.UNEXPECTED_SPLIT_RES_CODE)
