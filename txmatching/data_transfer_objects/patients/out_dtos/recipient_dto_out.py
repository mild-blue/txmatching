from dataclasses import dataclass
from typing import List, Optional, Dict

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.patients.patient import Recipient


@dataclass
class RecipientDTOOut(Recipient):
    all_messages: Optional[Dict[str, List[str]]] = None


@dataclass
class UpdatedRecipientDTOOut:
    recipient: RecipientDTOOut
    parsing_errors: List[ParsingError]
    overriding_error: bool
