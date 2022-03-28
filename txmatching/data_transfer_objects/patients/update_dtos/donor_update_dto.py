from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO


@dataclass
class DonorUpdateDTO(PatientUpdateDTO):
    active: Optional[bool] = None
    parsing_errors: Optional[List[ParsingError]] = None
