from typing import List, Union

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.patient import Patient
from kidney_exchange.patients.patient_parameters import PatientParameters


class Recipient(Patient):
    def __init__(self, patient_id: str, parameters: PatientParameters = None,
                 related_donors: Union[Donor, List[Donor]] = None):
        super().__init__(patient_id=patient_id, parameters=parameters)

        self._related_donors = related_donors

        if isinstance(related_donors, list) and len(related_donors) > 0:
            raise NotImplementedError("Multiple donors are not yet supported for one recipient")

    @property
    def related_donor(self) -> Donor:
        if self._related_donors is None:
            raise AssertionError("You have to set related donor")

        if isinstance(self._related_donors, List):
            return self._related_donors[0]  # TODO this is not implemented yet
        else:
            return self._related_donors
