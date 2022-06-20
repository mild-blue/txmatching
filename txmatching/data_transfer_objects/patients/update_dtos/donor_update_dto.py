from dataclasses import dataclass
from typing import Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO


@dataclass
class DonorUpdateDTO(PatientUpdateDTO):
    active: Optional[bool] = None

    def __post_init__(self):
        if self.height and self.height < 0:
            raise InvalidArgumentException(f'Invalid donor height {self.height}cm.')

        if self.weight and self.weight < 0:
            raise InvalidArgumentException(f'Invalid donor weight {self.weight}kg.')

        if self.year_of_birth and self.year_of_birth < 0:
            raise InvalidArgumentException(f'Invalid donor year of birth {self.year_of_birth}')
