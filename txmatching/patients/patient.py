from dataclasses import dataclass
from enum import Enum
from typing import List

from txmatching.patients.patient_parameters import PatientParameters


class DonorType(str, Enum):
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    ALTRUIST = 'ALTRUIST'


@dataclass
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters

    def is_recipient(self) -> bool:
        return isinstance(self, Recipient)

    def is_donor(self) -> bool:
        return isinstance(self, Donor)


@dataclass
class Donor(Patient):
    donor_type: DonorType = DonorType.DONOR


@dataclass
class Recipient(Patient):
    related_donor: Donor
    acceptable_blood_groups: List[str]


@dataclass
class DonorsRecipients:
    donors: List[Donor]
    recipients: List[Recipient]
