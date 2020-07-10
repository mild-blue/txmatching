from kidney_exchange.patients.patient_parameters import PatientParameters


class Patient:
    def __init__(self, patient_medical_id: str, parameters: PatientParameters = None):
        self._patient_medical_id = patient_medical_id
        self._parameters = parameters

    def __str__(self) -> str:
        return f"{{'id': '{self._patient_medical_id}', 'params': {str(self._parameters)}}}"

    def __hash__(self):
        return hash(self._patient_medical_id)

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self._patient_medical_id == other.medical_id

    @property
    def params(self):
        return self._parameters

    @property
    def medical_id(self) -> str:
        return self._patient_medical_id
