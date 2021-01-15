from dataclasses import dataclass
from typing import Optional

from txmatching.utils.hla_system.hla_transformations import parse_hla_raw_code


@dataclass
class HLAType:
    raw_code: str
    code: Optional[str] = None

    def __post_init__(self):
        if self.code is None:
            code = parse_hla_raw_code(self.raw_code)
            self.code = code

    def __eq__(self, other):
        """
        For List[HLAType].remove()
        """
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

# TODOO: move more here or move back
