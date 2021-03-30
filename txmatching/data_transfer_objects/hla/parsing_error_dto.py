from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsingError:
    hla_code: str
    hla_code_processing_result_detail: str
    message: str
    medical_id: Optional[str]  # TODOO: maybe req
    txm_event_id: Optional[int]
