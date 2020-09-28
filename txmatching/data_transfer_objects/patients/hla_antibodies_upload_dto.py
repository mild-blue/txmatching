from dataclasses import dataclass


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    mfi: int
    cutoff: int
