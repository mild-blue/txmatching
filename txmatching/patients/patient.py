from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict

from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient_types import RecipientDbId, DonorDbId


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
    related_recipient_db_id: Optional[RecipientDbId] = None
    donor_type: DonorType = DonorType.DONOR


@dataclass
class RecipientRequirements:
    """
    Attributes:
        require_new_donor_having_better_match_in_compatibility_index: New donor for recipient needs to have
        a better match in the compatibility index than (the best of) his original donor(s)
        require_new_donor_having_better_match_in_compatibility_index_or_blood_group: New donor for recipient
        has to have a better match in compatibility index or in blood group than (the best of) his original donor(s)
    """
    require_better_match_in_compatibility_index: Optional[bool] = None
    require_better_match_in_compatibility_index_or_blood_group: Optional[bool] = None
    require_compatible_blood_group: Optional[bool] = None


@dataclass
class Recipient(Patient):
    related_donor_db_id: DonorDbId
    acceptable_blood_groups: List[str]
    recipient_requirements: RecipientRequirements = RecipientRequirements()


@dataclass
class DonorsRecipients:
    donors_dict: Dict[DonorDbId, Donor]
    recipients_dict: Dict[RecipientDbId, Recipient]

    def to_lists_for_fe(self) -> Dict:
        return {
            "donors": list(self.donors_dict.values()),
            "recipients": list(self.recipients_dict.values())
        }
