from dataclasses import dataclass

from txmatching.patients.patient_parameters import PatientParameters


@dataclass
class PatientExcelDTO:
    medical_id: str
    parameters: PatientParameters
