from dataclasses import dataclass

from txmatching.utils.country import Country

PatientDbId = int


@dataclass
class ManualDonorRecipientScore:
    donor_db_id: int
    recipient_db_id: int
    score: float


@dataclass
class ForbiddenCountryCombination:
    donor_country: Country
    recipient_country: Country
