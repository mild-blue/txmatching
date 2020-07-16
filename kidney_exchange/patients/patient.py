from dataclasses import dataclass

from kidney_exchange.patients.patient_parameters import PatientParameters


@dataclass
class Patient:
    db_id: int
    medical_id: str
    parameters: PatientParameters

    @property
    def is_recipient(self) -> bool:
        raise NotImplementedError("Has to be overriden")


@dataclass
class PatientDto:
    medical_id: str
    parameters: PatientParameters
