from dataclasses import dataclass
from enum import Enum

from txmatching.patients.patient_parameters import PatientParameters


class PatientType(str, Enum):
    RECIPIENT = 'RECIPIENT'
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    ALTRUIST = 'ALTRUIST'

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
        if self.patient_type is not None:
            return self.patient_type.is_recipient_like()
        else:
            raise ValueError('patient type was None, which should never happened as it shall be defined in subclasses')
