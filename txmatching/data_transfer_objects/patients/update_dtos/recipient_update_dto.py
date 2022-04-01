from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.patient_update_dto import \
    PatientUpdateDTO
from txmatching.patients.patient import RecipientRequirements


# pylint: disable=too-many-instance-attributes
@dataclass
class RecipientUpdateDTO(PatientUpdateDTO):
    acceptable_blood_groups: Optional[List[str]] = None
    hla_antibodies: Optional[HLAAntibodiesUpdateDTO] = None
    recipient_requirements: Optional[RecipientRequirements] = None
    cutoff: Optional[int] = None
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None
