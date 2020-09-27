from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO


@dataclass
class DonorUpdateDTO:
    db_id: int
    hla_typing: Optional[HLATypingDTO] = None
