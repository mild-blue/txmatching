from dataclasses import dataclass

from kidney_exchange.web.data_transfer_objects.patient_dtos.donor_dto import DonorDTO
from kidney_exchange.web.data_transfer_objects.patient_dtos.patient_dto import PatientDTO


@dataclass
class RecipientDTO(PatientDTO):
    related_donor: DonorDTO
