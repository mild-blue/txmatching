from dataclasses import dataclass
from typing import Optional

from txmatching.patients.hla_code import HLACode
from txmatching.utils.hla_system.hla_transformations.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail


@dataclass
class HlaCodeProcessingResult:
    maybe_hla_code: Optional[HLACode]
    result_detail: HlaCodeProcessingResultDetail
