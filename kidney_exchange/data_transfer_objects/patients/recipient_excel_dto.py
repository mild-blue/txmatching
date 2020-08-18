from dataclasses import dataclass

from kidney_exchange.data_transfer_objects.patients.donor_excel_dto import \
    DonorDTO
from kidney_exchange.data_transfer_objects.patients.patient_excel_dto import \
    PatientExcelDTO


@dataclass
class RecipientDTO(PatientExcelDTO):
    related_donor: DonorDTO
