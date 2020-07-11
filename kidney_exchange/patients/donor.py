from dataclasses import dataclass

from kidney_exchange.patients.patient import Patient, PatientDto


@dataclass
class Donor(Patient):
    pass


@dataclass
class DonorDto(PatientDto):
    pass
