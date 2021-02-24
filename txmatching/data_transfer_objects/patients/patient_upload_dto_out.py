from dataclasses import dataclass
from typing import List


@dataclass
class PatientUploadDTOOut:
    recipients_uploaded: int
    donors_uploaded: int


@dataclass
class PatientsRecomputeParsingSuccessDTOOut:
    patients_checked: int
    patients_changed: int
    parsing_errors: List[dict]
