from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO
from txmatching.patients.patient import RecipientRequirements


@dataclass
class RecipientUpdateDTO:
    db_id: int
    acceptable_blood_groups: Optional[List[str]] = None
    hla_typing: Optional[HLATypingDTO] = None
    hla_antibodies: Optional[HLAAntibodiesDTO] = None
    recipient_requirements: Optional[RecipientRequirements] = None
