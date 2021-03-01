from dataclasses import dataclass
from typing import List


@dataclass
class PatientUploadDTOOut:
    recipients_uploaded: int
    donors_uploaded: int


@dataclass
class PatientsRecomputeParsingSuccessDTOOut:
    patients_checked_antigens: int
    patients_changed_antigens: int
    patients_checked_antibodies: int
    patients_changed_antibodies: int
    parsing_errors: List[dict]
