from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.patients.patient import Recipient


@dataclass
class RecipientDTOOut(Recipient):
    pass


@dataclass
class UpdatedRecipientDTOOut:
    recipient: RecipientDTOOut
    parsing_errors: List[ParsingError]
