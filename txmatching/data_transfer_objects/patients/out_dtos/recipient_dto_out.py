from dataclasses import dataclass
from typing import Dict, List, Optional

from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.patients.patient import Recipient


@dataclass
class RecipientDTOOut(Recipient):
    all_messages: Optional[Dict[str, List[ParsingIssue]]] = None


@dataclass
class UpdatedRecipientDTOOut:
    recipient: RecipientDTOOut
    parsing_issues: List[ParsingIssue]