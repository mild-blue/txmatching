from dataclasses import dataclass
from typing import List, Optional

from txmatching.patients.hla_code import HLACode
from txmatching.utils.enums import HLAGroup
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)


@dataclass
class HLABase:
    raw_code: str
    code: HLACode


@dataclass
class HLAType(HLABase, PersistentlyHashable):
    def __eq__(self, other):
        """
        Needed for List[HLAType].remove()
        """
        return isinstance(other, HLAType) and self.raw_code == other.raw_code

    def __hash__(self):
        return hash(self.raw_code)

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAType)
        update_persistent_hash(hash_, self.raw_code)


@dataclass
class HLATypeRaw:
    """
    Antigen in a format as uploaded without being parsed
    """
    raw_code: str


@dataclass
class HLATypeRawBothChains:
    """
    Antigen in a format as uploaded without being parsed, with the possibility of both chains being defined
    """
    raw_code: str
    secondary_raw_code: Optional[str] = None


@dataclass
class HLAPerGroup(PersistentlyHashable):
    hla_group: HLAGroup
    hla_types: List[HLAType]

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAPerGroup)
        update_persistent_hash(hash_, self.hla_group)
        update_persistent_hash(hash_, sorted(self.hla_types, key=lambda hla_type: hla_type.raw_code))


@dataclass
class HLATyping(PersistentlyHashable):
    hla_types_raw_list: List[HLATypeRaw]
    hla_per_groups: List[HLAPerGroup]

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLATyping)
        update_persistent_hash(hash_, self.hla_per_groups)


@dataclass
class HLAAntibody(HLABase, PersistentlyHashable):
    mfi: int
    cutoff: int
    secondary_raw_code: Optional[str] = None

    def __eq__(self, other):
        return (isinstance(other, HLAAntibody) and
                self.raw_code == other.raw_code and
                self.mfi == other.mfi and
                self.cutoff == other.cutoff and
                self.secondary_raw_code == other.secondary_raw_code)

    def __hash__(self):
        return hash((self.raw_code, self.mfi, self.cutoff, self.secondary_raw_code))

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAAntibody)
        update_persistent_hash(hash_, self.raw_code)
        update_persistent_hash(hash_, self.mfi)
        update_persistent_hash(hash_, self.cutoff)
        update_persistent_hash(hash_, self.secondary_raw_code)


@dataclass
class HLAAntibodyRaw:
    raw_code: str
    mfi: int
    cutoff: int


@dataclass
class AntibodiesPerGroup(PersistentlyHashable):
    hla_group: HLAGroup
    hla_antibody_list: List[HLAAntibody]

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, AntibodiesPerGroup)
        update_persistent_hash(hash_, self.hla_group)
        update_persistent_hash(
            hash_,
            sorted(
                self.hla_antibody_list,
                key=lambda hla_type: (
                    hla_type.raw_code,
                    hla_type.mfi,
                    hla_type.cutoff
                )
            )
        )


@dataclass
class HLAAntibodies(PersistentlyHashable):
    hla_antibodies_raw_list: List[HLAAntibodyRaw]
    hla_antibodies_per_groups: List[AntibodiesPerGroup]

    @property
    def hla_antibodies_per_groups_over_cutoff(self) -> List[AntibodiesPerGroup]:
        return _filter_antibodies_per_groups_over_cutoff(self.hla_antibodies_per_groups)

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAAntibodies)
        update_persistent_hash(hash_, self.hla_antibodies_per_groups)


def _filter_antibodies_per_groups_over_cutoff(
        hla_antibodies_per_groups: List[AntibodiesPerGroup]
) -> List[AntibodiesPerGroup]:
    return [
        AntibodiesPerGroup(
            hla_group=antibodies_per_group.hla_group,
            hla_antibody_list=_filter_antibodies_over_cutoff(
                antibodies_per_group.hla_antibody_list
            )
        ) for antibodies_per_group in hla_antibodies_per_groups
    ]


def _filter_antibodies_over_cutoff(
        hla_antibodies: List[HLAAntibody]
) -> List[HLAAntibody]:
    return [
        hla_antibody for hla_antibody in hla_antibodies
        if hla_antibody.mfi >= hla_antibody.cutoff
    ]
