from dataclasses import dataclass
from typing import Optional

from txmatching.patients.patient_parameters import HLATyping


@dataclass
class DonorUpdateDTO:
    db_id: int
    hla_typing: Optional[HLATyping] = None
