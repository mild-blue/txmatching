from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass
class DonorUploadDTO:
    # pylint: disable=too-many-instance-attributes
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    donor_type: str
    related_recipient_medical_id: Optional[str]
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: str = ''
    internal_medical_id: Optional[str] = None

    def __post_init__(self):
        if self.height and self.height < 0:
            raise InvalidArgumentException(f'Invalid donor height {self.height}cm.')

        if self.year_of_birth and (self.year_of_birth < 1900 or self.year_of_birth > date.today().year):
            raise InvalidArgumentException(f'Invalid donor year of birth {self.year_of_birth}')

        if self.weight and self.weight < 0:
            raise InvalidArgumentException(f'Invalid donor weight {self.weight}kg.')
