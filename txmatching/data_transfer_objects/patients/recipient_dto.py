from dataclasses import dataclass

from txmatching.data_transfer_objects.patients.donor_dto import DonorDTO
from txmatching.data_transfer_objects.patients.patient_dto import PatientDTO


@dataclass
class RecipientDTO(PatientDTO):
    related_donor: DonorDTO
