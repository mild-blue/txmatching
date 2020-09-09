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
class RecipientRequirements:
    """
    Attributes:
        require_new_donor_having_better_match_in_compatibility_index: New donor for recipient needs to have
        a better match in the compatibility index than (the best of) his original relative(s)
        require_new_donor_having_better_match_in_compatibility_index_or_blood_group: New donor for recipient
        has to have a better match in compatibility index or in blood group than (the best of) his original relative(s)
    """
    require_better_match_in_compatibility_index: bool = False
    require_better_match_in_compatibility_index_or_blood_group: bool = False
    require_compatible_blood_group: bool = False


@dataclass
class Recipient(Patient):
    related_donor: Donor
    acceptable_blood_groups: List[str]
    recipient_requirements: RecipientRequirements = RecipientRequirements()


@dataclass
class DonorsRecipients:
    donors: List[Donor]
    recipients: List[Recipient]
