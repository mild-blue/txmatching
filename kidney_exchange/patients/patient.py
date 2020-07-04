from kidney_exchange.patients.patient_parameters import PatientParameters


class Patient:
    def __init__(self, patient_id: str, parameters: PatientParameters = None):
        self._patient_id = patient_id
        self._parameters = parameters

    def __str__(self) -> str:
        return f"{{'id': '{self._patient_id}', 'params': {str(self._parameters)}}}"

    def __hash__(self):
        return hash(self._patient_id)

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self._patient_id == other.patient_id

    @property
    def params(self):
        return self._parameters

    @property
    def patient_id(self) -> str:
        return self._patient_id
