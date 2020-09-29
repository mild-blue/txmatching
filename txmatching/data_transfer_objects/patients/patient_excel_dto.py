from dataclasses import dataclass

from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    PatientParametersDTO


@dataclass
class PatientExcelDTO:
    medical_id: str
    parameters: PatientParametersDTO
