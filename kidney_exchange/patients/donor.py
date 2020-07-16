from dataclasses import dataclass

from kidney_exchange.patients.patient import Patient, PatientDto


@dataclass
class Donor(Patient):
    pass

    @property
    def is_recipient(self) -> bool:
        return False


@dataclass
class DonorDto(PatientDto):
    pass
