from dataclasses import dataclass
from typing import List, Optional

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
    recipient_id: Optional[str] = None
    recipient_sample_id: Optional[str] = None
    donor_code: Optional[str] = None
    donor_sample_id: Optional[str] = None
    datetime: Optional[str] = None


@dataclass
class CrossmatchDTOOut:
    # pylint: disable=too-many-instance-attributes
    hla_to_antibody: List[AntibodyMatchForHLAType]
    parsing_issues: List[ParsingIssueBase]
    is_positive_crossmatch: bool
    recipient_id: Optional[str] = None
    recipient_sample_id: Optional[str] = None
    donor_code: Optional[str] = None
    donor_sample_id: Optional[str] = None
    datetime: Optional[str] = None


@dataclass
class CPRACalculationDTOIn:
    hla_antibodies: List[HLAAntibodiesUploadDTO]
    patient_id: Optional[str] = None
    sample_id: Optional[str] = None
    datetime: Optional[str] = None


@dataclass
class CPRACalculationDTOOut:
    patient_id: str
    sample_id: str
    datetime: str
    parsed_antibodies: HLAAntibodies
    parsing_issues: List[ParsingIssueBase]
    cpra: float
