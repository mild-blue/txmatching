from dataclasses import dataclass, field
from typing import List, Optional

from kidney_exchange.utils.hla_system.high_resolution_to_low_resolution import hla_high_to_low_res, \
    is_valid_low_res_code


@dataclass
class HLAAntigens:
    codes: List[str] = field(default_factory=list)


@dataclass
class HLAAntibodies:
    codes: List[str] = field(default_factory=list)


@dataclass
class PatientParameters:
    blood_group: Optional[str] = None
    acceptable_blood_groups: List[str] = field(default_factory=list)
    hla_antigens: HLAAntigens = HLAAntigens()
    hla_antibodies: HLAAntibodies = HLAAntibodies()
    country_code: Optional[str] = None

    @property
    def hla_antigens_low_resolution(self) -> List[str]:
        low_res_codes = [hla_high_to_low_res(antigen) for antigen in self.hla_antigens.codes]
        low_res_codes = [code for code in low_res_codes if is_valid_low_res_code(code)]
        return low_res_codes

    @property
    def hla_antibodies_low_resolution(self) -> List[str]:
        low_res_codes = [hla_high_to_low_res(antibody) for antibody in self.hla_antibodies.codes]
        low_res_codes = [code for code in low_res_codes if is_valid_low_res_code(code)]
        return low_res_codes
