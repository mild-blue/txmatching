from dataclasses import dataclass

from typing import List, Optional


@dataclass
class DonorUploadDTO:
    # pylint: disable=too-many-instance-attributes
    medical_id: str
    blood_group: str
    HLA_typing: List[str]  # pylint: disable=invalid-name
    donor_type: str
    related_recipient_medical_id: Optional[str]
    sex: Optional[str]
    height: Optional[int]
    weight: Optional[int]
    YOB: Optional[int]  # pylint: disable=invalid-name
