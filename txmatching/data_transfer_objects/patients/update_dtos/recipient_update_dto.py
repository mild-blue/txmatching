from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.patients.patient import (is_height_valid, is_number_of_previous_transplants_valid,
    is_weight_valid, is_year_of_birth_valid, RecipientRequirements)


# pylint: disable=too-many-instance-attributes
# pylint: disable=duplicate-code
@dataclass
class RecipientUpdateDTO(PatientUpdateDTO):
    acceptable_blood_groups: Optional[List[str]] = None
    hla_antibodies: Optional[HLAAntibodiesUpdateDTO] = None
    recipient_requirements: Optional[RecipientRequirements] = None
    cutoff: Optional[int] = None
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        if self.height:
            is_height_valid("recipient", self.height)

        if self.weight:
            is_weight_valid("recipient", self.weight)

        if self.year_of_birth:
            is_year_of_birth_valid("recipient", self.year_of_birth)

        if self.previous_transplants:
            is_number_of_previous_transplants_valid(self.previous_transplants)
