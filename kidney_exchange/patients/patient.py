from dataclasses import dataclass
from enum import Enum

from kidney_exchange.patients.patient_parameters import PatientParameters


class PatientType(Enum):
    RECIPIENT = 1
    DONOR = 2
    BRIDGING_DONOR = 3
    ALTRUIST = 4

    def is_donor_like(self):
        return self in {PatientType.DONOR, PatientType.ALTRUIST, PatientType.BRIDGING_DONOR}

    def is_recipient_like(self):
        return self in {PatientType.RECIPIENT}

@dataclass
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters
    patient_type = None  # Not part of constructor, has to be defined elsewhere

    @property
    def is_recipient(self) -> bool:
        if self.patient_type is None:
            raise ValueError(f"patient type was None, which should never happend as it shall be defined in subclasses")
        else:
            return self.patient_type.is_recipient_like()


@dataclass
class PatientDto:
    medical_id: str
    parameters: PatientParameters
