from dataclasses import dataclass


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    MFI: int
    cutoff: int
