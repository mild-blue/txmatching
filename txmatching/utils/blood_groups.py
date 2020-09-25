from enum import Enum

from txmatching.patients.patient import Recipient, Donor

COMPATIBLE_BLOOD_GROUPS = {
    "0": {"0"},
    "A": {"0", "A"},
    "B": {"0", "B"},
    "AB": {"0", "A", "B", "AB"}
}


class HLATypes(Enum):
    A = "A"
    B = "B"
    DR = "DR"


ANTIBODIES_MULTIPLIERS = {
    HLATypes.A: 1,
    HLATypes.B: 2,
    HLATypes.DR: 9
}

ANTIBODIES_MULTIPLIERS_STR = {
    HLATypes.A.value: 1,
    HLATypes.B.value: 2,
    HLATypes.DR.value: 9
}


def blood_groups_compatible(donor: Donor, recipient: Recipient) -> bool:
    return donor.parameters.blood_group in COMPATIBLE_BLOOD_GROUPS[recipient.parameters.blood_group]
