from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.patients.patient_excel_dto import \
    PatientExcelDTO


@dataclass
class RecipientExcelDTO(PatientExcelDTO):
    acceptable_blood_groups: List[str]
