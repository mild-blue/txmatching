from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class TransplantWarningDetail(str, Enum):
    # donor weight
    MAX_WEIGHT = lambda max_weight: (
        f'The donor is heavier than {max_weight}kg, that is the maximum allowable weight of'
        ' the donor specified in the recipient requirements.')
    MIN_WEIGHT = lambda min_weight: (
        f'The donor is lighter than {min_weight}kg, that is the minimum allowable weight of'
        ' the donor specified in the recipient requirements.')

    # donor height
    MAX_HEIGHT = lambda max_height: (f'The donor is taller than {max_height}cm, that is the maximum allowable height of'
                                     ' the donor specified in the recipient requirements.')
    MIN_HEIGHT = lambda min_height: (
        f'The donor is smaller than {min_height}cm, that is the minimum allowable height of'
        ' the donor specified in the recipient requirements.')

    # donor age
    MAX_AGE = lambda max_age: (f'The donor is older than {max_age} years, that is the maximum allowable age of the donor'
                               ' specified in the recipient requirements.')
    MIN_AGE = lambda min_age: (f'The donor is younger than {min_age} years, that is the minimum allowable age of the donor'
                               ' specified in the recipient requirements.')

    # possible crossmatch
    BROAD_CROSSMATCH = lambda antibodies: (
        f'There is a possible crossmatch on broad level for antibodies: {antibodies}.'
        ' The tranplant should be confirmed with immunologist first')
    SPLIT_CROSSMATCH = lambda antibodies: (
        f'There is a possible crossmatch on split level for antibodies: {antibodies}.'
        ' The tranplant should be confirmed with immunologist first')
    # todo: should I add warning messages also for missing antibodies and missing typization?

@dataclass
class TransplantWarnings:
    message_global: str
    all_messages: Dict[str, List[TransplantWarningDetail]]
