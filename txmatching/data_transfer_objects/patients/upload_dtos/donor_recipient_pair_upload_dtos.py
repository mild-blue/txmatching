from dataclasses import dataclass
from typing import List, Optional

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.patients.patient_parameters import Centimeters, Kilograms
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex


@dataclass
class HLAAntibodiesFromPairDTO:
    name: str
    mfi: int

# pylint: disable=too-many-instance-attributes
@dataclass
class RecipientFromPairDTO:
    acceptable_blood_groups: Optional[List[BloodGroup]]
    medical_id: str
    blood_group: BloodGroup
    hla_typing: List[str]
    recipient_cutoff: int
    hla_antibodies: List[HLAAntibodiesFromPairDTO]
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    waiting_since: Optional[str] = None
    previous_transplants: Optional[int] = None

    def to_upload_dto(self) -> RecipientUploadDTO:
        return RecipientUploadDTO(
            year_of_birth=self.year_of_birth,
            hla_typing=self.hla_typing,
            weight=self.weight,
            sex=self.sex,
            height=self.height,
            waiting_since=self.waiting_since,
            hla_antibodies=[HLAAntibodiesUploadDTO(
                name=antibody.name,
                mfi=antibody.mfi,
                cutoff=self.recipient_cutoff
            ) for antibody in self.hla_antibodies],
            previous_transplants=self.previous_transplants,
            acceptable_blood_groups=self.acceptable_blood_groups,
            blood_group=self.blood_group,
            medical_id=self.medical_id
        )


@dataclass
class DonorRecipientPairDTO:
    country_code: Country
    donor: DonorUploadDTO
    recipient: RecipientFromPairDTO
