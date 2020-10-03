from dataclasses import dataclass


@dataclass
class HLAAntibodiesUploadDTO:
    name: str
    MFI: int  # pylint: disable=invalid-name
    cutoff: int
