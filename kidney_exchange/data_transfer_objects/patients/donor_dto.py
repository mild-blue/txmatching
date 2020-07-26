from dataclasses import dataclass

from kidney_exchange.data_transfer_objects.patients.patient_dto import PatientDTO


@dataclass
class DonorDTO(PatientDTO):
    pass
