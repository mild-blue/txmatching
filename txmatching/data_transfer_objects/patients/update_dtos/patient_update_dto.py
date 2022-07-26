from dataclasses import dataclass
from typing import Optional

from txmatching.data_transfer_objects.patients.patient_base_dto import (
    PatientBaseDTO, RecipientBaseDTO)
from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import \
    HLATypingUpdateDTO
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass(kw_only=True)
class PatientUpdateDTO(PatientBaseDTO, RecipientBaseDTO):
    # pylint: disable=too-many-instance-attributes
    # It is reasonable to have many attributes here
    db_id: int
    etag: int
    blood_group: Optional[BloodGroup] = None
    hla_typing: Optional[HLATypingUpdateDTO] = None
    sex: Optional[Sex] = None
    note: Optional[str] = None
