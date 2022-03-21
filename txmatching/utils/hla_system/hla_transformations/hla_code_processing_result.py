from dataclasses import dataclass
from typing import Optional

from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail


@dataclass
class HlaCodeProcessingResult:
    maybe_hla_code: Optional[HLACode]
    result_detail: ParsingIssueDetail
