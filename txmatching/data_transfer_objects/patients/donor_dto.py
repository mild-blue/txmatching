from dataclasses import dataclass

from txmatching.data_transfer_objects.patients.patient_dto import PatientDTO


@dataclass
class DonorDTO(PatientDTO):
    pass
