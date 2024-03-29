from dataclasses import dataclass
from typing import Dict, List, Optional

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.patients.patient import Donor
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup


@dataclass
class DonorDTOOut(Donor):
    all_messages: Optional[Dict[str, List[ParsingIssue]]] = None
    score_with_related_recipient: Optional[float] = None
    max_score_with_related_recipient: Optional[float] = None
    detailed_score_with_related_recipient: Optional[List[DetailedScoreForHLAGroup]] = None
    compatible_blood_with_related_recipient: Optional[str] = None
    # this attribute has default value because fields without default values cannot appear
    # after fields with default values. That is why we check if this attribute is set during init
    active_and_valid_pair: bool = None

    def __post_init__(self):
        if self.active_and_valid_pair is None:
            raise InvalidArgumentException('Active and valid pair attribute should be set.')


@dataclass
class UpdatedDonorDTOOut:
    donor: DonorDTOOut
    parsing_issues: List[ParsingIssue]
