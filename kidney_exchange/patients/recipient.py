from typing import List, Union

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient


class Recipient(Patient):
    def __init__(self, id: str, related_donors: Union[Donor, List[Donor]] = None):
        super().__init__(id)

        self._related_donors = related_donors

        if len(related_donors) > 0:
            raise NotImplementedError("Multiple donors are not yet supported for one recipient")

    @property
    def related_donor(self) -> Donor:
        if self._related_donors is None:
            raise AssertionError("You have to set related donor")

        if isinstance(self._related_donors, List):
            return self._related_donors[0]
        else:
            return self._related_donors
