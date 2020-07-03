from kidney_exchange.patients.patient_parameters import PatientParameters


class Patient:
    def __init__(self, id: str, parameters: PatientParameters = None):
        self._id = id
        self._parameters = parameters

    def __str__(self) -> str:
        return f"{self._id} | {str(self._parameters)}"

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self._id == other._id

    @property
    def params(self):
        return self._parameters
