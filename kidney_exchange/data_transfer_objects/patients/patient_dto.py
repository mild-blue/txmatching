from dataclasses import dataclass

from kidney_exchange.patients.patient import PatientType
from kidney_exchange.patients.patient_parameters import PatientParameters


@dataclass
class PatientDTO:
    medical_id: str
    patient_type: PatientType
    parameters: PatientParameters
