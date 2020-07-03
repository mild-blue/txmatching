from typing import List

from kidney_exchange.utils.hla_system.high_resolution_to_low_resolution import hla_high_to_low_res, \
    is_valid_low_res_code


class PatientParameters:
    def __init__(self, blood_group: str = None, acceptable_blood_groups: List[str] = None,
                 hla_antigens: List[str] = None, hla_antibodies: List[str] = None,
                 country_code: str = None):
        self._blood_group = blood_group
        self._acceptable_blood_groups = acceptable_blood_groups
        self._hla_antigens = hla_antigens
        self._hla_antibodies = hla_antibodies
        self._country_code = country_code

    def __str__(self) -> str:
        acceptable_blood_groups_str = "" if self._acceptable_blood_groups is None \
            else f"({', '.join(self._acceptable_blood_groups)})"

        return f"{self._country_code} | {self._blood_group} {acceptable_blood_groups_str} | " \
               f"antigens: {str(self._hla_antigens)} | antibodies: {str(self._hla_antibodies)}"

    @property
    def blood_group(self) -> str:
        return self._blood_group

    @property
    def acceptable_blood_groups(self) -> List[str]:
        return self._acceptable_blood_groups

    @property
    def country_code(self) -> str:
        return self._country_code

    @property
    def hla_antigens_low_resolution(self) -> List[str]:
        low_res_codes = [hla_high_to_low_res(antigen) for antigen in self._hla_antigens]
        low_res_codes = [code for code in low_res_codes if is_valid_low_res_code(code)]
        return low_res_codes

    @property
    def hla_antibodies_low_resolution(self) -> List[str]:
        low_res_codes = [hla_high_to_low_res(antibody) for antibody in self._hla_antibodies]
        low_res_codes = [code for code in low_res_codes if is_valid_low_res_code(code)]
        return low_res_codes
