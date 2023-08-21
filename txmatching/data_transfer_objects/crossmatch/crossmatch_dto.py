from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.hla_model import (HLAAntibodies,
                                           HLATypeWithFrequencyRaw)
from txmatching.utils.hla_system.hla_cadaverous_crossmatch import \
    AntibodyMatchForHLAType


@dataclass
class CrossmatchDTOIn:
    potential_donor_hla_typing: List[List[HLATypeWithFrequencyRaw]]
    recipient_antibodies: List[HLAAntibodiesUploadDTO]


@dataclass
class CrossmatchDTOOut:
    hla_to_antibody: List[AntibodyMatchForHLAType]
    parsing_issues: List[ParsingIssueBase]
    is_positive_crossmatch: bool


@dataclass
class CPRACalculationDTOIn:
    hla_antibodies: List[HLAAntibodiesUploadDTO]


@dataclass
class CPRACalculationDTOOut:
    parsed_antibodies: HLAAntibodies
    parsing_issues: List[ParsingIssueBase]
    cpra: float
