from dataclasses import dataclass

from txmatching.patients.patient_parameters import PatientParameters


@dataclass
class PatientDTO:
    medical_id: str
    parameters: PatientParameters
