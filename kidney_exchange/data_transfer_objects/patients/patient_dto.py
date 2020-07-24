from dataclasses import dataclass

from kidney_exchange.patients.patient_parameters import PatientParameters


@dataclass
class PatientDTO:
    medical_id: str
    parameters: PatientParameters
