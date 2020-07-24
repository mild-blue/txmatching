from dataclasses import dataclass

from kidney_exchange.web.data_transfer_objects.patient_dtos.patient_dto import PatientDTO


@dataclass
class DonorDTO(PatientDTO):
    pass
