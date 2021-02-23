from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex
from txmatching.utils.hla_system.hla_transformations import \
    preprocess_hla_codes_in


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
