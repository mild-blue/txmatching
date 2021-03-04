from dataclasses import dataclass
from typing import Optional


@dataclass
class HLACode:
    display_code: str

    high_res: Optional[str]
    split: Optional[str]
    broad: str

    @property
    def split_or_broad(self) -> str:
        return self.split if self.split is not None else self.broad

    def __init__(self, high_res: Optional[str], split: Optional[str], broad: str, display_code: str = None):
        # display_code: Currently display_code is stored in db as well and we need to have this parameter in
        #   the constructor so that dacite.from_dict would work. We have display_code here because we want to send it
        #   to FE
        self.high_res = high_res
        self.split = split
        self.broad = broad

        if high_res is not None and split is None:
            raise ValueError(f'High res was specified ({high_res}) but split was not specified')

        # Set display code
        if high_res is not None:
            self.display_code = high_res
        elif split is not None:
            self.display_code = split
        else:
            self.display_code = broad

    def __repr__(self):
        return f'HLACode({repr(self.high_res)}, {repr(self.split)}, {repr(self.broad)})'

    def __hash__(self):
        return hash((self.high_res, self.split, self.broad))
