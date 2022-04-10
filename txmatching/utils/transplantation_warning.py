from dataclasses import dataclass

from enum import Enum
from typing import List, Dict


class TransplantWarningDetail(str, Enum):
    # donor weight
    MAX_WEIGHT = 'The donor is heavier than the maximum allowable weight of the donor specified in the recipient requirements.'
    MIN_WEIGHT = 'The donor is lighter than the minimum allowable weight of the donor specified in the recipient requirements.'

    # donor height
    MAX_HEIGHT = 'The donor is taller than the maximum allowable height of the donor specified in the recipient requirements.'
    MIN_HEIGHT = 'The donor is smaller than the minimum allowable height of the donor specified in the recipient requirements.'

    # donor age
    MAX_AGE = 'The donor is older than the maximum allowable age of the donor specified in the recipient requirements.'
    MIN_AGE = 'The donor is younger than the minimum allowable age of the donor specified in the recipient requirements.'


@dataclass
class TransplantWarnings:
    message_global: str
    all_messages: Dict[str, List[TransplantWarningDetail]]
