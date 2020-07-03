from typing import List

from kidney_exchange.utils.hla_system.high_resolution_to_low_resolution import hla_high_to_low_res


class PatientParameters:
    def __init__(self, blood_group: str = None, acceptable_blood_groups: List[str] = None,
                 hla_antigens: List[str] = None, hla_antibodies: List[str] = None):
        self._blood_group = blood_group
        self._acceptable_blood_groups = acceptable_blood_groups
        self._hla_antigens = hla_antigens
        self._hla_antibodies = hla_antibodies

    @property
    def blood_group(self) -> str:
        return self._blood_group

    @property
    def acceptable_blood_groups(self) -> List[str]:
        return self._acceptable_blood_groups

    @property
    def hla_antigens_low_resolution(self) -> List[str]:
        return [hla_high_to_low_res(antigen) for antigen in self._hla_antigens]

    @property
    def hla_antibodies_low_resolution(self) -> List[str]:
        return [hla_high_to_low_res(antibody) for antibody in self._hla_antibodiesself._hla_antibodies]
