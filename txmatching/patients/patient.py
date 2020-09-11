from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

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
    related_recipient_db_id: Optional[int] = None
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
    related_donor_db_id: int
    acceptable_blood_groups: List[str]
    recipient_requirements: RecipientRequirements = RecipientRequirements()


@dataclass
class DonorsRecipients:
    donors_dict: Dict[int, Donor]
    recipients_dict: Dict[int, Recipient]

    def to_lists_for_fe(self) -> Dict:
        return {
            "donors": list(self.donors_dict.values()),
            "recipients": list(self.recipients_dict.values())
        }
