from dataclasses import dataclass, field
from typing import List

from txmatching.utils.country import Country
from txmatching.utils.hla_system.hla_table import hla_split_to_broad, is_valid_broad_code


@dataclass
class HLATyping:
    codes: List[str] = field(default_factory=list)

    @property
    def hla_typing_broad_resolution(self) -> List[str]:
        broad_res_codes = [hla_split_to_broad(antigen) for antigen in self.codes]
        broad_res_codes = [code for code in broad_res_codes if is_valid_broad_code(code)]
        return broad_res_codes


@dataclass
class HLAAntibodies:
    codes: List[str] = field(default_factory=list)

    @property
    def hla_antibodies_broad_resolution(self) -> List[str]:
        broad_res_codes = [hla_split_to_broad(antibody) for antibody in self.codes]
        broad_res_codes = [code for code in broad_res_codes if is_valid_broad_code(code)]
        return broad_res_codes


@dataclass
class PatientParameters:
    blood_group: str
    country_code: Country
    hla_typing: HLATyping = HLATyping()
