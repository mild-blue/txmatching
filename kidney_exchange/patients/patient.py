from kidney_exchange.patients.patient_parameters import PatientParameters


class Patient:
    def __init__(self, id: str, parameters: PatientParameters = None):
        self._id = id
        self._parameters = parameters

    @property
    def params(self):
        return self._parameters
