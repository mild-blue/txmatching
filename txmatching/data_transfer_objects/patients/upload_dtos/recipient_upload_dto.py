from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.patient_base_dto import (
    PatientBaseDTO, RecipientBaseDTO)
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Sex


@dataclass(kw_only=True)
class RecipientUploadDTO(PatientBaseDTO, RecipientBaseDTO):
    # pylint: disable=too-many-instance-attributes
    acceptable_blood_groups: Optional[List[BloodGroup]]
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    sex: Optional[Sex] = None
    note: str = ''
    waiting_since: Optional[str] = None
    internal_medical_id: Optional[str] = None
