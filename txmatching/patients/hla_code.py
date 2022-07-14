import re

from dataclasses import dataclass
from typing import Optional

from txmatching.utils.enums import GENE_HLA_GROUPS_WITH_OTHER_DETAILED, HLA_GROUPS_PROPERTIES, HLAGroup


@dataclass
class HLACode:
    high_res: Optional[str]
    split: Optional[str]
    broad: Optional[str]
    group: Optional[HLAGroup]

    @property
    def display_code(self) -> str:
        if self.high_res is not None:
            return self.high_res
        elif self.split is not None:
            return self.split
        elif self.broad is not None:
            return self.broad
        else:
            raise AssertionError('This should never happen. At least one code should be specified.')

    def __init__(self, high_res: Optional[str], split: Optional[str], broad: Optional[str], group = None):
        assert high_res is not None or broad is not None
        self.high_res = high_res
        self.split = split
        self.broad = broad
        self.group = self.group_from_hla_code

    def __repr__(self):
        return f'HLACode({repr(self.high_res)}, {repr(self.split)}, {repr(self.broad)})'

    def __hash__(self):
        return hash((self.high_res, self.split, self.broad))

    @property
    def group_from_hla_code(self) -> Optional[HLAGroup]:
        for hla_group in GENE_HLA_GROUPS_WITH_OTHER_DETAILED:
            if self._is_raw_code_in_group(hla_group):
                return hla_group
        return None

    def _is_raw_code_in_group(self, hla_group: HLAGroup) -> bool:
        if self.broad is not None:
            return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, self.broad))
        elif self.high_res is not None:
            return bool(re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, self.high_res))
        else:
            raise AssertionError(f'Broad or high res should be provided: {self}')
