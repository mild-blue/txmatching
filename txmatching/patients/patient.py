from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibodyRaw
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import TxmEventState
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
    parsing_errors: Optional[List[ParsingError]] = None
    related_recipient_db_id: Optional[RecipientDbId] = None
    donor_type: DonorType = DonorType.DONOR
    active: bool = True
    internal_medical_id: Optional[str] = None

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Donor)
        # TODO this is not hashable:
        # update_persistent_hash(hash_, sorted(self.parsing_errors))
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


# pylint: disable=too-many-instance-attributes
@dataclass
class Recipient(Patient, PersistentlyHashable):
    related_donor_db_id: DonorDbId
    acceptable_blood_groups: List[BloodGroup]
    hla_antibodies: HLAAntibodies
    parsing_errors: Optional[List[ParsingError]] = None
    recipient_cutoff: Optional[int] = None
    recipient_requirements: RecipientRequirements = RecipientRequirements()
    waiting_since: Optional[datetime] = None
    previous_transplants: Optional[int] = None
    internal_medical_id: Optional[str] = None

    def __post_init__(self):
        if self.recipient_cutoff is None:
            self.recipient_cutoff = calculate_cutoff(self.hla_antibodies.hla_antibodies_raw_list)

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Recipient)
        update_persistent_hash(hash_, self.related_donor_db_id)
        update_persistent_hash(hash_, sorted(self.acceptable_blood_groups))
        # TODO this is not hashable:
        # update_persistent_hash(hash_, sorted(self.parsing_errors))
        update_persistent_hash(hash_, self.recipient_cutoff)
        update_persistent_hash(hash_, self.hla_antibodies)
        update_persistent_hash(hash_, self.recipient_requirements)
        update_persistent_hash(hash_, self.waiting_since)
        update_persistent_hash(hash_, self.previous_transplants)


@dataclass
class TxmEventBase:
    db_id: int
    name: str
    default_config_id: Optional[int]
    state: TxmEventState


@dataclass(init=False)
class TxmEvent(TxmEventBase):
    all_donors: List[Donor]
    all_recipients: List[Recipient]
    active_and_valid_donors_dict: Dict[DonorDbId, Donor]
    active_and_valid_recipients_dict: Dict[RecipientDbId, Recipient]

    # pylint: disable=too-many-arguments
    # I think it is reasonable to have multiple arguments here
    def __init__(self, db_id: int, name: str, default_config_id: Optional[int], state: TxmEventState,
                 all_donors: List[Donor], all_recipients: List[Recipient]):
        super().__init__(db_id=db_id, name=name, default_config_id=default_config_id, state=state)
        self.all_donors = all_donors
        self.all_recipients = all_recipients
        (
            self.active_and_valid_donors_dict,
            self.active_and_valid_recipients_dict,
        ) = _filter_patients_that_dont_have_parsing_errors(all_donors, all_recipients)


def calculate_cutoff(hla_antibodies_raw_list: List[HLAAntibodyRaw]) -> int:
    """
    Calculates patient cutoff.
    :param hla_antibodies_raw_list: list of HLA raw antibodies.
    :return: Patient cutoff.
    """
    helper_raw_code = 'A1'
    return max(hla_antibodies_raw_list,
               key=lambda antibody: antibody.cutoff,
               default=HLAAntibodyRaw(
                   raw_code=helper_raw_code,
                   mfi=0,
                   cutoff=DEFAULT_CUTOFF
               )).cutoff


def _filter_patients_that_dont_have_parsing_errors(
    donors: List[Donor], recipients: List[Recipient]
    ) -> (Dict[DonorDbId, Donor], Dict[RecipientDbId, Recipient]):
    exclude_donors_ids = set()
    exclude_recipients_ids = set()

    for patient in donors:
        if not _parsing_error_list_is_empty(patient.parsing_errors):
            exclude_donors_ids.add(patient.db_id)
            if patient.related_recipient_db_id is not None:
                exclude_recipients_ids.add(patient.related_recipient_db_id)

    for patient in recipients:
        if not _parsing_error_list_is_empty(patient.parsing_errors):
            if patient.db_id not in exclude_recipients_ids:
                exclude_donors_ids.add(patient.related_donor_db_id)
                exclude_recipients_ids.add(patient.db_id)

    return_donors = {
        patient.db_id: patient
        for patient in donors
        if patient.db_id not in exclude_donors_ids and patient.active
    }
    return_recipients = {
        patient.db_id: patient
        for patient in recipients
        if patient.db_id not in exclude_recipients_ids and patient.related_donor_db_id in return_donors
    }

    return return_donors, return_recipients


def _parsing_error_list_is_empty(parsing_errors: List[ParsingError]) -> bool:
    if parsing_errors is not None and len(parsing_errors) > 0:
        return False
    return True
