from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import \
    HLATypingUpdateDTO


@dataclass
class PatientUpdateDTO:
    db_id: int
    hla_typing: Optional[HLATypingUpdateDTO] = None
