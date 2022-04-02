from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import \
    HLATypingUpdateDTO
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass
class PatientUpdateDTO:
    # pylint: disable=too-many-instance-attributes
    # It is reasonable to have many attributes here
    db_id: int
    blood_group: Optional[BloodGroup] = None
    hla_typing: Optional[HLATypingUpdateDTO] = None
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: Optional[str] = None
