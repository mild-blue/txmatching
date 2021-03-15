from dataclasses import dataclass
from typing import Optional


@dataclass
class HLACode:
    high_res: Optional[str]
    split: Optional[str]
    broad: Optional[str]

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

    def __init__(self, high_res: Optional[str], split: Optional[str], broad: Optional[str]):
        assert high_res is not None or split is not None or broad is not None
        self.high_res = high_res
        self.split = split
        self.broad = broad

    def __repr__(self):
        return f'HLACode({repr(self.high_res)}, {repr(self.split)}, {repr(self.broad)})'

    def __hash__(self):
        return hash((self.high_res, self.split, self.broad))
