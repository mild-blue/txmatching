from dataclasses import dataclass

from kidney_exchange.patients.patient import Patient, PatientType


@dataclass
class Donor(Patient):
    patient_type: PatientType = PatientType.DONOR

    @property
    def is_recipient(self) -> bool:
        return False
