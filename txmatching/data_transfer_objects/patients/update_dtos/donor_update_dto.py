from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.patients.patient import is_height_valid, is_weight_valid, is_year_of_birth_valid


# pylint: disable=duplicate-code
@dataclass
class DonorUpdateDTO(PatientUpdateDTO):
    active: Optional[bool] = None

    def __post_init__(self):
        if self.height:
            is_height_valid("donor", self.height)

        if self.weight:
            is_weight_valid("donor", self.weight)

        if self.year_of_birth:
            is_year_of_birth_valid("donor", self.year_of_birth)
