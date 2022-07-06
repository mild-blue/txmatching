from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)


@dataclass
class ParsingIssuePublicDTO:
    hla_code_or_group: Optional[str]
    parsing_issue_detail: str
    message: str
    txm_event_name: Optional[str]
    medical_id: Optional[str]
    confirmed_by: Optional[int]
    confirmed_at: Optional[datetime]


# pylint: disable=too-many-instance-attributes
@dataclass
class ParsingIssue(PersistentlyHashable):
    hla_code_or_group: Optional[str]
    parsing_issue_detail: ParsingIssueDetail
    message: str
    txm_event_id: Optional[int] = None
    donor_id: Optional[int] = None
    recipient_id: Optional[int] = None
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[datetime] = None

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, ParsingIssue)
        update_persistent_hash(hash_, self.hla_code_or_group)
        update_persistent_hash(hash_, self.parsing_issue_detail.name)
        update_persistent_hash(hash_, self.message)
        update_persistent_hash(hash_, self.txm_event_id)
        update_persistent_hash(hash_, self.donor_id)
        update_persistent_hash(hash_, self.recipient_id)
        update_persistent_hash(hash_, self.confirmed_by)
        update_persistent_hash(hash_, self.confirmed_at)


# pylint: disable=too-many-instance-attributes
@dataclass
class ParsingIssueConfirmationDTO:
    db_id: int
    hla_code_or_group: Optional[str]
    parsing_issue_detail: str
    message: str
    confirmed_by: Optional[int]
    confirmed_at: Optional[datetime]
    txm_event_id: Optional[int] = None
    donor_id: Optional[int] = None
    recipient_id: Optional[int] = None
