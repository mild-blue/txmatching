from enum import Enum


class BloodGroup(str, Enum):
    A = 'A'
    B = 'B'
    AB = 'AB'
    ZERO = '0'

    @classmethod
    def _missing_(cls, name):
        if name in {0, 'O'}:
            return cls.ZERO
        raise ValueError(f'{name} is not a valid BloodGroup')


COMPATIBLE_BLOOD_GROUPS = {
    BloodGroup.ZERO: {BloodGroup.ZERO},
    BloodGroup.A: {BloodGroup.ZERO, BloodGroup.A},
    BloodGroup.B: {BloodGroup.ZERO, BloodGroup.B},
    BloodGroup.AB: {BloodGroup.ZERO, BloodGroup.A, BloodGroup.B, BloodGroup.AB}
}


def blood_groups_compatible(donor_blood: BloodGroup, recipient_blood: BloodGroup) -> bool:
    return donor_blood in COMPATIBLE_BLOOD_GROUPS[recipient_blood]
