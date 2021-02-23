import itertools
from dataclasses import dataclass
from typing import List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
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
        # TODOO: antibodies

        self.hla_antibodies_preprocessed = [
            HLAAntibodiesUploadDTO(parsed_code, hla_antibody_in.mfi, hla_antibody_in.cutoff)
            for hla_antibody_in in self.hla_antibodies
            for parsed_code in preprocess_hla_code_in(hla_antibody_in.name)
        ]
        grouped_hla_antibodies = itertools.groupby(sorted(self.hla_antibodies_preprocessed, key=lambda x: x.name),
                                                   key=lambda x: x.name)
        for hla_code_raw, antibody_group in grouped_hla_antibodies:
            cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group}
            if len(cutoffs) > 1:
                raise InvalidArgumentException(f'There were multiple cutoff values for antibody {hla_code_raw} '
                                               'This means inconsistency that is not allowed.')
