from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.patient import RecipientRequirements
from txmatching.patients.patient_parameters import HLAAntibodies, HLATyping


@dataclass
class RecipientUpdateDTO:
    db_id: int
    acceptable_blood_groups: Optional[List[str]] = None
    hla_typing: Optional[HLATyping] = None
    hla_antibodies: Optional[HLAAntibodies] = None
    recipient_requirements: Optional[RecipientRequirements] = None
