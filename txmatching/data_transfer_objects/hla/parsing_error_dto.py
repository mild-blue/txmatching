from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsingError:
    hla_code_or_group: Optional[str]
    parsing_issue_detail: str
    message: str
    medical_id: Optional[str]
    txm_event_id: Optional[int]
