import dataclasses
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.patients.hla_model import HLAAntibodies, HLAAntibodyRaw
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import TxmEventState
from txmatching.utils.hla_system.hla_crossmatch import \
    is_positive_hla_crossmatch
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import (
    ERROR_PROCESSING_RESULTS, WARNING_PROCESSING_RESULTS)
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)

DEFAULT_CUTOFF = 2000


class DonorType(str, Enum):
    DONOR = 'DONOR'
    BRIDGING_DONOR = 'BRIDGING_DONOR'
    NON_DIRECTED = 'NON_DIRECTED'

    def __format__(self, format_spec):
        return f'{self.name}'


@dataclass
class Patient(PersistentlyHashable):
    db_id: int
    medical_id: str
    parameters: PatientParameters
    etag: int

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
    parsing_issues: Optional[List[ParsingIssue]] = None
    related_recipient_db_id: Optional[RecipientDbId] = None
    donor_type: DonorType = DonorType.DONOR
    active: bool = True
    internal_medical_id: Optional[str] = None

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Donor)
        # TODO this is not hashable:
        # update_persistent_hash(hash_, sorted(self.parsing_issues))
        update_persistent_hash(hash_, self.related_recipient_db_id)
        update_persistent_hash(hash_, self.donor_type)
        update_persistent_hash(hash_, self.active)


# pylint: disable=too-many-instance-attributes
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
    max_donor_weight: Optional[float] = None
    min_donor_weight: Optional[float] = None
    max_donor_height: Optional[int] = None
    min_donor_height: Optional[int] = None
    max_donor_age: Optional[int] = None
    min_donor_age: Optional[int] = None

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, RecipientRequirements)
        # Treat None as False
        update_persistent_hash(hash_, bool(self.require_better_match_in_compatibility_index_or_blood_group))
        update_persistent_hash(hash_, bool(self.require_better_match_in_compatibility_index))
        update_persistent_hash(hash_, bool(self.require_compatible_blood_group))
        update_persistent_hash(hash_, self.max_donor_weight)
        update_persistent_hash(hash_, self.min_donor_weight)
        update_persistent_hash(hash_, self.max_donor_height)
        update_persistent_hash(hash_, self.min_donor_height)
        update_persistent_hash(hash_, self.max_donor_age)
        update_persistent_hash(hash_, self.min_donor_age)


# pylint: disable=too-many-instance-attributes
@dataclass
class Recipient(Patient, PersistentlyHashable):
    related_donors_db_ids: List[DonorDbId]
    acceptable_blood_groups: List[BloodGroup]
    hla_antibodies: HLAAntibodies
    parsing_issues: Optional[List[ParsingIssue]] = None
    recipient_cutoff: Optional[int] = None
    recipient_requirements: RecipientRequirements = dataclasses.field(default_factory=
                                                                      RecipientRequirements)
    waiting_since: Optional[datetime] = None
    previous_transplants: Optional[int] = None
    internal_medical_id: Optional[str] = None

    def __post_init__(self):
        if self.recipient_cutoff is None:
            self.recipient_cutoff = calculate_cutoff(self.hla_antibodies.hla_antibodies_raw_list)

    def update_persistent_hash(self, hash_: HashType):
        super().update_persistent_hash(hash_)
        update_persistent_hash(hash_, Recipient)
        update_persistent_hash(hash_, sorted(self.related_donors_db_ids))
        update_persistent_hash(hash_, sorted(self.acceptable_blood_groups))
        # TODO this is not hashable:
        # update_persistent_hash(hash_, sorted(self.parsing_issues))
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
        ) = _filter_patients_that_dont_have_parsing_errors_or_unconfirmed_warnings(all_donors, all_recipients)


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


def calculate_cpra_and_get_compatible_donors_for_recipient(txm_event: TxmEvent, recipient: Recipient,
                                                           config_parameters: Optional[ConfigParameters]) \
        -> Tuple[int, Set[int]]:
    """
    Calculates cPRA for recipient (which part of donors [as decimal] is compatible) for actual txm_event.
    :return: cPRA as decimal in [0;1].
    """
    active_donors = txm_event.active_and_valid_donors_dict.values()
    if len(active_donors) == 0:  # no donors = compatible to all donors
        return 1, set()

    compatible_donors = set()
    for donor in active_donors:
        if not is_positive_hla_crossmatch(donor_hla_typing=donor.parameters.hla_typing,
                                          recipient_antibodies=recipient.hla_antibodies,
                                          use_high_resolution=config_parameters.use_high_resolution,
                                          crossmatch_level=config_parameters.hla_crossmatch_level):
            # crossmatch test is negative -> donor is compatible to recipient
            compatible_donors.add(donor.db_id)

    return 1 - len(compatible_donors)/len(active_donors), compatible_donors


def _filter_patients_that_dont_have_parsing_errors_or_unconfirmed_warnings(
        donors: List[Donor], recipients: List[Recipient]
) -> Tuple[Dict[DonorDbId, Donor], Dict[RecipientDbId, Recipient]]:
    exclude_donors_ids = set()
    exclude_recipients_ids = set()

    for patient in donors:
        if (_parsing_issue_list_contains_errors(patient.parsing_issues) or
                _parsing_issue_list_contains_unconfirmed_warnings(patient.parsing_issues)):
            exclude_donors_ids.add(patient.db_id)

    for patient in recipients:
        if (_parsing_issue_list_contains_errors(patient.parsing_issues) or
                _parsing_issue_list_contains_unconfirmed_warnings(patient.parsing_issues)):
            for donor_id in patient.related_donors_db_ids:
                exclude_donors_ids.add(donor_id)
            exclude_recipients_ids.add(patient.db_id)

    return_donors = {
        patient.db_id: patient
        for patient in donors
        if patient.db_id not in exclude_donors_ids and patient.active
    }
    return_recipients = {
        patient.db_id: patient
        for patient in recipients
        if patient.db_id not in exclude_recipients_ids and _recipient_has_at_least_one_active_donor(
            patient.related_donors_db_ids, return_donors)
    }

    return return_donors, return_recipients


def _recipient_has_at_least_one_active_donor(related_donors_db_ids: List[int],
                                             return_donors: Dict[DonorDbId, Donor]) -> bool:
    for donor_db_id in related_donors_db_ids:
        if donor_db_id in return_donors:
            return True
    return False


def _parsing_issue_list_contains_errors(parsing_issues: Optional[List[ParsingIssue]]) -> bool:
    if parsing_issues is None:
        return False
    for parsing_issue in parsing_issues:
        if parsing_issue.parsing_issue_detail in ERROR_PROCESSING_RESULTS:
            return True
    return False


def _parsing_issue_list_contains_unconfirmed_warnings(parsing_issues: Optional[List[ParsingIssue]]) -> bool:
    if parsing_issues is None:
        return False
    for parsing_issue in parsing_issues:
        if parsing_issue.parsing_issue_detail in WARNING_PROCESSING_RESULTS and parsing_issue.confirmed_at is None:
            return True
    return False
