from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.hla.parsing_error_dto import (
    ParsingError, ParsingErrorPublicDTO)


@dataclass
class PatientUploadPublicDTOOut:
    recipients_uploaded: int
    donors_uploaded: int
    parsing_errors: List[ParsingErrorPublicDTO]


@dataclass
class PatientsRecomputeParsingSuccessDTOOut:
    patients_checked_antigens: int
    patients_changed_antigens: int
    patients_checked_antibodies: int
    patients_changed_antibodies: int
    parsing_errors: List[ParsingError]
