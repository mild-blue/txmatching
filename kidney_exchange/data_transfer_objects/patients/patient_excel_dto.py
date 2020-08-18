from dataclasses import dataclass

from kidney_exchange.patients.patient_parameters import PatientParameters


@dataclass
class PatientExcelDTO:
    medical_id: str
    parameters: PatientParameters
