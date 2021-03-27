from dataclasses import dataclass

from txmatching.utils.country_enum import Country

PatientDbId = int


@dataclass(frozen=True)
class ManualDonorRecipientScore:
    donor_db_id: int
    recipient_db_id: int
    score: float


@dataclass(frozen=True)
class ForbiddenCountryCombination:
    donor_country: Country
    recipient_country: Country
