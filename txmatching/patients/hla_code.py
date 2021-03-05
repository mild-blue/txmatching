from dataclasses import dataclass
from typing import Optional


@dataclass
class HLACode:
    high_res: Optional[str]
    split: Optional[str]
    broad: str

    @property
    def split_or_broad(self) -> str:
        return self.split if self.split is not None else self.broad

    @property
    def display_code(self) -> str:
        if self.high_res is not None:
            return self.high_res
        elif self.split is not None:
            return self.split
        else:
            return self.broad

    def __init__(self, high_res: Optional[str], split: Optional[str], broad: str):
        self.high_res = high_res
        self.split = split
        self.broad = broad

    def __repr__(self):
        return f'HLACode({repr(self.high_res)}, {repr(self.split)}, {repr(self.broad)})'

    def __hash__(self):
        return hash((self.high_res, self.split, self.broad))
