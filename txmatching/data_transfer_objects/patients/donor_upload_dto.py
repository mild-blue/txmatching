from dataclasses import dataclass

from typing import List


@dataclass
class DonorUploadDTO:
    # pylint: disable=too-many-instance-attributes
    medical_id: str
    blood_group: str
    hla_typing: List[str]
    donor_type: str
    related_recipient_medical_id: str
    sex: str
    height: int
    weight: int
    yob: int
