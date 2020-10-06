from dataclasses import dataclass
from typing import List

from txmatching.data_transfer_objects.patients.patient_excel_dto import \
    PatientExcelDTO
from txmatching.patients.patient_parameters import HLAAntibodies
from txmatching.utils.blood_groups import BloodGroup


@dataclass
class RecipientExcelDTO(PatientExcelDTO):
    hla_antibodies: HLAAntibodies
    acceptable_blood_groups: List[BloodGroup]
    recipient_cutoff: int
