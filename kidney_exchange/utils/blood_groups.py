from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient

COMPATIBLE_BLOOD_GROUPS = {
    "0": {"0"},
    "A": {"0", "A"},
    "B": {"0", "B"},
    "AB": {"0", "A", "B", "AB"}
}


def blood_groups_compatible(donor: Donor, recipient: Recipient) -> bool:
    return donor.parameters.blood_group in COMPATIBLE_BLOOD_GROUPS[recipient.parameters.blood_group]
