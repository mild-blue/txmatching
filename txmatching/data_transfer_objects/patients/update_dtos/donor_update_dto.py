from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO


@dataclass
class DonorUpdateDTO(PatientUpdateDTO):
    active: Optional[bool] = None
