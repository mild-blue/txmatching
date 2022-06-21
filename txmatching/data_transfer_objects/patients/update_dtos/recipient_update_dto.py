from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.patients.patient import RecipientRequirements


# pylint: disable=too-many-instance-attributes
@dataclass
class RecipientUpdateDTO(PatientUpdateDTO):
    acceptable_blood_groups: Optional[List[str]] = None
    hla_antibodies: Optional[HLAAntibodiesUpdateDTO] = None
    recipient_requirements: Optional[RecipientRequirements] = None
    cutoff: Optional[int] = None
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        if self.height and self.height < 0:
            raise InvalidArgumentException(f'Invalid recipient height {self.height}cm.')

        if self.weight and self.weight < 0:
            raise InvalidArgumentException(f'Invalid recipient weight {self.weight}kg.')

        if self.year_of_birth and (self.year_of_birth < 1900 or self.year_of_birth > date.today().year):
            raise InvalidArgumentException(f'Invalid recipient year of birth {self.year_of_birth}')

        if self.previous_transplants and self.previous_transplants < 0:
            raise InvalidArgumentException(
                f'Invalid recipient number of previous transplants {self.previous_transplants}.')
