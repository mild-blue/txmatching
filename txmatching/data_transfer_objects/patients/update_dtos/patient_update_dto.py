from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO
from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import \
    HLATypingUpdateDTO
from txmatching.patients.patient_parameters import HLAType
from txmatching.utils.hla_system.hla_transformations import \
    preprocess_hla_code_in


@dataclass
class PatientUpdateDTO:
    db_id: int
    hla_typing: Optional[HLATypingUpdateDTO] = None

    def __post_init__(self):
        if self.hla_typing:
            self.hla_typing_preprocessed = HLATypingDTO([
                HLAType(parsed_code)
                for hla_type_update_dto in self.hla_typing.hla_types_list
                for parsed_code in preprocess_hla_code_in(hla_type_update_dto.raw_code)
            ])
