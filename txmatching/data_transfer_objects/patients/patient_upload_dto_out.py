from dataclasses import dataclass


@dataclass
class PatientUploadDTOOut:
    recipients_uploaded: int
    donors_uploaded: int
