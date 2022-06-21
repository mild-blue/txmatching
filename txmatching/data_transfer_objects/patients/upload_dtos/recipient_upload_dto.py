from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass
class RecipientUploadDTO:
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[BloodGroup]]
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: str = ''
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None
    internal_medical_id: Optional[str] = None

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
