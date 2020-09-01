from dataclasses import dataclass

from txmatching.data_transfer_objects.patients.patient_excel_dto import \
    PatientExcelDTO


@dataclass
class DonorDTO(PatientExcelDTO):
    pass
