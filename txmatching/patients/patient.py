from dataclasses import dataclass
from enum import Enum
from typing import List

from txmatching.patients.patient_parameters import PatientParameters


class PatientType(str, Enum):
    RECIPIENT = 'RECIPIENT'
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    ALTRUIST = 'ALTRUIST'

    def is_donor_like(self):
        return self in {PatientType.DONOR, PatientType.ALTRUIST, PatientType.BRIDGING_DONOR}

    def is_recipient_like(self):
        return self in {PatientType.RECIPIENT}


@dataclass
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters
    patient_type: PatientType

    def is_recipient(self) -> bool:
        return isinstance(self, Recipient)

    def is_donor(self) -> bool:
        return isinstance(self, Donor)


@dataclass
class Donor(Patient):
    def __post_init__(self):
        if not self.patient_type.is_donor_like():
            raise ValueError('Wrong patient type for donor')


@dataclass
class Recipient(Patient):
    related_donor: Donor
    acceptable_blood_groups: List[str]

    def __post_init__(self):
        if not self.patient_type.is_recipient_like():
            raise ValueError('Wrong patient type for recipient')


@dataclass
class DonorsRecipients:
    donors: List[Donor]
    recipients: List[Recipient]
