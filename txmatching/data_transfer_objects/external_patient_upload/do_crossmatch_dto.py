from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssueBase
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatch


@dataclass
class CrossmatchDTOIn:
    donor_hla_typing: List[str]
    recipient_antibodies: List[HLAAntibodiesUploadDTO]


@dataclass
class HLAToAntibodyMatch:
    hla_code: str
    antibody_matches: List[AntibodyMatch] = None


@dataclass
class CrossmatchDTOOut:
    hla_to_antibody: HLAToAntibodyMatch
    parsing_issues: List[ParsingIssueBase]
