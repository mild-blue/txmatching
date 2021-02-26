from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from txmatching.patients.hla_model import HLAAntibodies, HLAAntibody
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)

DEFAULT_CUTOFF = 2000


class DonorType(str, Enum):
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    NON_DIRECTED = 'NON_DIRECTED'


@dataclass
class Patient(PersistentlyHashable):
    db_id: int
    medical_id: str
    parameters: PatientParameters

    def is_recipient(self) -> bool:
        return isinstance(self, Recipient)

    def is_donor(self) -> bool:
        return isinstance(self, Donor)

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, Patient)
        update_persistent_hash(hash_, self.medical_id)
        update_persistent_hash(hash_, self.parameters)


@dataclass
class Donor(Patient, PersistentlyHashable):
    related_recipient_db_id: Optional[RecipientDbId] = None
    donor_type: DonorType = DonorType.DONOR
    active: bool = True

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Donor)
        update_persistent_hash(hash_, self.related_recipient_db_id)
        update_persistent_hash(hash_, self.donor_type)
        update_persistent_hash(hash_, self.active)


@dataclass
class RecipientRequirements(PersistentlyHashable):
    """
    Attributes:
    require_better_match_in_compatibility_index: New donor for recipient needs to have a better match in the
    compatibility index than (the best of) his original donor(s)
    require_better_match_in_compatibility_index_or_blood_group: New donor for recipient has to have a better match in
    compatibility index or in blood group than (the best of) his original donor(s)
    require_compatible_blood_group: New donor needs to have compatible blood group using the standard schema
    """
    require_better_match_in_compatibility_index: Optional[bool] = None
    require_better_match_in_compatibility_index_or_blood_group: Optional[bool] = None
    require_compatible_blood_group: Optional[bool] = None

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, RecipientRequirements)
        # Treat None as False
        update_persistent_hash(hash_, bool(self.require_better_match_in_compatibility_index_or_blood_group))
        update_persistent_hash(hash_, bool(self.require_better_match_in_compatibility_index))
        update_persistent_hash(hash_, bool(self.require_compatible_blood_group))


@dataclass
class Recipient(Patient, PersistentlyHashable):
    related_donor_db_id: DonorDbId
    acceptable_blood_groups: List[BloodGroup]
    recipient_cutoff: Optional[int] = None
    hla_antibodies: HLAAntibodies = HLAAntibodies([])
    recipient_requirements: RecipientRequirements = RecipientRequirements()
    waiting_since: Optional[datetime] = None
    previous_transplants: Optional[int] = None

    def __post_init__(self):
        if self.recipient_cutoff is None:
            self.recipient_cutoff = calculate_cutoff(self.hla_antibodies.hla_antibodies_list)

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Recipient)
        update_persistent_hash(hash_, self.related_donor_db_id)
        update_persistent_hash(hash_, sorted(self.acceptable_blood_groups))
        update_persistent_hash(hash_, self.recipient_cutoff)
        update_persistent_hash(hash_, self.hla_antibodies)
        update_persistent_hash(hash_, self.recipient_requirements)
        update_persistent_hash(hash_, self.waiting_since)
        update_persistent_hash(hash_, self.previous_transplants)


@dataclass
class TxmEventBase:
    db_id: int
    name: str


@dataclass(init=False)
class TxmEvent(TxmEventBase):
    all_donors: List[Donor]
    all_recipients: List[Recipient]
    active_donors_dict: Dict[DonorDbId, Donor]
    active_recipients_dict: Dict[RecipientDbId, Recipient]

    def __init__(self, db_id: int, name: str, all_donors: List[Donor], all_recipients: List[Recipient]):
        self.db_id = db_id
        self.name = name
        self.all_donors = all_donors
        self.all_recipients = all_recipients
        self.active_donors_dict = {donor.db_id: donor for donor in self.all_donors if donor.active}
        self.active_recipients_dict = {recipient.db_id: recipient for recipient in self.all_recipients if
                                       recipient.related_donor_db_id in self.active_donors_dict}


def calculate_cutoff(hla_antibodies_list: List[HLAAntibody]) -> int:
    """
    Calculates patient cutoff.
    :param hla_antibodies_list: list of HLA antibodies.
    :return: Patient cutoff.
    """
    helper_raw_code = 'A1'
    helper_code = 'A1'
    return max(hla_antibodies_list,
               key=lambda antibody: antibody.cutoff,
               default=HLAAntibody(
                   raw_code=helper_raw_code,
                   mfi=0,
                   cutoff=DEFAULT_CUTOFF,
                   code=helper_code
               )).cutoff
