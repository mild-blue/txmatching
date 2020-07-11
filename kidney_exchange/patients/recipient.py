from dataclasses import dataclass

from kidney_exchange.patients.donor import Donor, DonorDto
from kidney_exchange.patients.patient import Patient, PatientDto


@dataclass
class Recipient(Patient):
    related_donor: Donor


@dataclass
class RecipientDto(PatientDto):
    related_donor: DonorDto
