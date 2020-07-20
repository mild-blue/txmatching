from dataclasses import dataclass

from kidney_exchange.patients.patient import Patient, PatientDto, PatientType


@dataclass
class Donor(Patient):
    patient_type: PatientType = PatientType.DONOR
    pass

    @property
    def is_recipient(self) -> bool:
        return False


@dataclass
class DonorDto(PatientDto):
    pass
