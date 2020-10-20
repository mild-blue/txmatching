from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import (
    HLAAntibodiesDTO, HLAAntibodyDTO)
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.patients.patient import RecipientRequirements
from txmatching.utils.hla_system.hla_transformations import \
    preprocess_hla_code_in


# pylint: disable=too-many-instance-attributes
@dataclass
class RecipientUpdateDTO(PatientUpdateDTO):
    acceptable_blood_groups: Optional[List[str]] = None
    hla_antibodies: Optional[HLAAntibodiesDTO] = None
    recipient_requirements: Optional[RecipientRequirements] = None
    cutoff: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        if self.hla_antibodies:
            self.hla_antibodies_preprocessed = HLAAntibodiesDTO([
                HLAAntibodyDTO(preprocess_code, hla_antibody_dto.mfi)
                for hla_antibody_dto in self.hla_antibodies.hla_antibodies_list
                for preprocess_code in preprocess_hla_code_in(hla_antibody_dto.raw_code)
            ])
