from dataclasses import dataclass
from typing import Optional

from txmatching.patients.hla_model import HLATyping
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Sex
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)

Kilograms = float
Centimeters = int


@dataclass
class PatientParameters(PersistentlyHashable):
    blood_group: BloodGroup
    country_code: Country
    hla_typing: HLATyping
    sex: Optional[Sex] = None
    height: Optional[Centimeters] = None
    weight: Optional[Kilograms] = None
    year_of_birth: Optional[int] = None
    note: str = ''

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, PatientParameters)
        update_persistent_hash(hash_, self.blood_group)
        update_persistent_hash(hash_, self.country_code)
        update_persistent_hash(hash_, self.hla_typing)
        update_persistent_hash(hash_, self.sex)
        update_persistent_hash(hash_, self.height)
        update_persistent_hash(hash_, self.weight)
        update_persistent_hash(hash_, self.year_of_birth)
