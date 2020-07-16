from dataclasses import dataclass

from kidney_exchange.patients.patient_parameters import PatientParameters


@dataclass
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters

    def __hash__(self):
        return hash(self._patient_medical_id)

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self._patient_medical_id == other.medical_id

    @property
    def is_recipient(self) -> bool:
        raise NotImplementedError("Has to be overriden")


@dataclass
class PatientDto:
    medical_id: str
    parameters: PatientParameters
