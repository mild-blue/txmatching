from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex
from txmatching.utils.hla_system.hla_transformations import (
    preprocess_hla_code_in, preprocess_hla_codes_in)


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
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        self.hla_typing_preprocessed = preprocess_hla_codes_in(self.hla_typing)
        self.hla_antibodies_preprocessed = [
            HLAAntibodiesUploadDTO(parsed_code, hla_antibody_in.mfi, hla_antibody_in.cutoff)
            for hla_antibody_in in self.hla_antibodies
            for parsed_code in preprocess_hla_code_in(hla_antibody_in.name)
        ]
