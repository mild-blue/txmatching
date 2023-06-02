from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssueBase
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO
from txmatching.patients.hla_model import AssumedHLATypeRaw
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatchForHLAType


@dataclass
class CrossmatchDTOIn:
    potential_donor_hla_typing: List[List[AssumedHLATypeRaw]]
    recipient_antibodies: List[HLAAntibodiesUploadDTO]

    def get_maximum_donor_hla_typing(self):
        return [hla_type.hla_code for hla_typing in self.potential_donor_hla_typing
                for hla_type in hla_typing]


@dataclass
class CrossmatchDTOOut:
    hla_to_antibody: List[AntibodyMatchForHLAType]
    parsing_issues: List[ParsingIssueBase]
