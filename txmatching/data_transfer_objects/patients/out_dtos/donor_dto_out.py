from dataclasses import dataclass
from typing import List, Optional, Dict

from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssueConfirmationDTO
from txmatching.patients.patient import Donor
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup


@dataclass
class DonorDTOOut(Donor):
    all_messages: Optional[Dict[str, List[ParsingIssueConfirmationDTO]]] = None
    score_with_related_recipient: Optional[float] = None
    max_score_with_related_recipient: Optional[float] = None
    detailed_score_with_related_recipient: Optional[List[DetailedScoreForHLAGroup]] = None
    compatible_blood_with_related_recipient: Optional[str] = None


@dataclass
class UpdatedDonorDTOOut:
    donor: DonorDTOOut
    parsing_issues: List[ParsingIssueConfirmationDTO]
