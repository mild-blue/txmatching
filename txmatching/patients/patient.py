from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code

DEFAULT_CUTOFF = 2000


class DonorType(str, Enum):
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    NON_DIRECTED = 'NON_DIRECTED'


@dataclass(unsafe_hash=True)
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters

    def is_recipient(self) -> bool:
        return isinstance(self, Recipient)

    def is_donor(self) -> bool:
        return isinstance(self, Donor)


@dataclass(unsafe_hash=True)
class Donor(Patient):
    related_recipient_db_id: Optional[RecipientDbId] = None
    donor_type: DonorType = DonorType.DONOR
    active: bool = True


@dataclass(unsafe_hash=True)
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
    acceptable_blood_groups: List[BloodGroup]
    recipient_cutoff: Optional[int] = None
    hla_antibodies: HLAAntibodies = HLAAntibodies()
    recipient_requirements: RecipientRequirements = RecipientRequirements()
    waiting_since: Optional[datetime] = None
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        if self.recipient_cutoff is None:
            self.recipient_cutoff = calculate_cutoff(self.hla_antibodies.hla_antibodies_list)

    def __hash__(self):
        return hash((
            *self.acceptable_blood_groups,
            self.recipient_cutoff,
            self.hla_antibodies,
            self.recipient_requirements,
            self.waiting_since,
            self.previous_transplants
        ))


@dataclass
class TxmEvent:
    db_id: int
    name: str
    all_donors: List[Donor]
    all_recipients: List[Recipient]
    active_donors_dict: Optional[Dict[DonorDbId, Donor]] = None
    active_recipients_dict: Optional[Dict[RecipientDbId, Recipient]] = None

    def __post_init__(self):
        if not self.active_donors_dict:
            self.active_donors_dict = {donor.db_id: donor for donor in self.all_donors if donor.active}
        if not self.active_recipients_dict:
            self.active_recipients_dict = {recipient.db_id: recipient for recipient in self.all_recipients if
                                           recipient.related_donor_db_id in self.active_donors_dict}


def calculate_cutoff(hla_antibodies_list: List[HLAAntibody]) -> int:
    """
    Calculates patient cutoff.
    :param hla_antibodies_list: list of HLA antibodies.
    :return: Patient cutoff.
    """
    helper_raw_code = 'A1'
    return max(hla_antibodies_list,
               key=lambda antibody: antibody.cutoff,
               default=HLAAntibody(
                   raw_code=helper_raw_code,
                   mfi=0,
                   cutoff=DEFAULT_CUTOFF,
                   code=parse_hla_raw_code(helper_raw_code)
               )).cutoff
