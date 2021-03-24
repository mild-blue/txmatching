from dataclasses import dataclass

from txmatching.patients.patient import Recipient


@dataclass
class RecipientDTOOut(Recipient):
    pass
