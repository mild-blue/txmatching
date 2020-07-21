from dataclasses import dataclass

from kidney_exchange.patients.donor import Donor, DonorDto
from kidney_exchange.patients.patient import Patient, PatientDto, PatientType


@dataclass
class Recipient(Patient):
    related_donor: Donor
    patient_type: PatientType = PatientType.RECIPIENT

    @property
    def is_recipient(self) -> bool:
        return True


@dataclass
class RecipientDto(PatientDto):
    related_donor: DonorDto
