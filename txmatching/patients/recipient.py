from dataclasses import dataclass

from txmatching.patients.donor import Donor
from txmatching.patients.patient import Patient, PatientType


@dataclass
class Recipient(Patient):
    related_donor: Donor
    patient_type: PatientType = PatientType.RECIPIENT

    @property
    def is_recipient(self) -> bool:
        return True
