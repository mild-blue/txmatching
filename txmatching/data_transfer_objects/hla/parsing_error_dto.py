from dataclasses import dataclass
from typing import Optional

from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)


@dataclass
class ParsingErrorPublicDTO:
    hla_code_or_group: Optional[str]
    parsing_issue_detail: str
    message: str
    txm_event_name: Optional[str]
    medical_id: Optional[str]


@dataclass
class ParsingError(PersistentlyHashable):
    hla_code_or_group: Optional[str]
    parsing_issue_detail: ParsingIssueDetail
    message: str
    txm_event_id: Optional[int] = None
    donor_id: Optional[int] = None
    recipient_id: Optional[int] = None

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, ParsingError)
        update_persistent_hash(hash_, self.hla_code_or_group)
        update_persistent_hash(hash_, self.parsing_issue_detail.name)
        update_persistent_hash(hash_, self.message)
        update_persistent_hash(hash_, self.txm_event_id)
        update_persistent_hash(hash_, self.donor_id)
        update_persistent_hash(hash_, self.recipient_id)
