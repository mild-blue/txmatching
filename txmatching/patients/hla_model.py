import itertools
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Union

from txmatching.patients.hla_code import HLACode
from txmatching.utils.enums import (HLA_GROUP_HIGH_RES_CODE_REGEX,
                                    HLA_GROUP_SPLIT_CODE_REGEX,
                                    HLA_GROUPS_NAMES_WITH_OTHER, HLAGroup)
from txmatching.utils.hla_system.hla_transformations.get_mfi_from_multiple_hla_codes import \
    get_mfi_from_multiple_hla_codes
from txmatching.utils.logging_tools import PatientAdapter
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)


@dataclass
class HLAType(PersistentlyHashable):
    raw_code: str
    code: HLACode

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
class HLAAntibody(PersistentlyHashable):
    raw_code: str
    code: HLACode
    mfi: int
    cutoff: int

    def __eq__(self, other):
        return (isinstance(other, HLAAntibody) and
                self.raw_code == other.raw_code and
                self.mfi == other.mfi and
                self.cutoff == other.cutoff)

    def __hash__(self):
        return hash((self.raw_code, self.mfi, self.cutoff))

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAAntibody)
        update_persistent_hash(hash_, self.raw_code)
        update_persistent_hash(hash_, self.mfi)
        update_persistent_hash(hash_, self.cutoff)


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


def split_hla_types_to_groups(hla_types: List[HLAType]) -> List[HLAPerGroup]:
    hla_types_in_groups = _split_hla_types_to_groups(hla_types)
    return [HLAPerGroup(hla_group,
                        sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                        ) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]


def create_hla_antibodies_per_groups_from_hla_antibodies(
        hla_antibodies: List[HLAAntibody],
        logger_with_patient: Union[logging.Logger, PatientAdapter] = logging.getLogger(__name__)
) -> List[AntibodiesPerGroup]:
    hla_antibodies_joined = _join_duplicate_antibodies(hla_antibodies, logger_with_patient)
    hla_antibodies_per_groups = _split_antibodies_to_groups(hla_antibodies_joined)
    return hla_antibodies_per_groups


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


def _split_antibodies_to_groups(hla_antibodies: List[HLAAntibody]) -> List[AntibodiesPerGroup]:
    hla_antibodies_in_groups = _split_hla_types_to_groups(hla_antibodies)
    return [AntibodiesPerGroup(hla_group,
                               sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                               ) for hla_group, hla_codes_in_group in
            hla_antibodies_in_groups.items()]


def _join_duplicate_antibodies(
        hla_antibodies: List[HLAAntibody],
        logger_with_patient: Union[logging.Logger, PatientAdapter]
) -> List[HLAAntibody]:
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    grouped_hla_antibodies = itertools.groupby(sorted(hla_antibodies, key=_group_key),
                                               key=_group_key)
    hla_antibodies_joined = []
    for hla_code_raw, antibody_group in grouped_hla_antibodies:
        antibody_group_list = list(antibody_group)
        assert len(antibody_group_list) > 0
        cutoffs = {hla_antibody.cutoff for hla_antibody in antibody_group_list}
        if len(cutoffs) != 1:
            raise AssertionError(f'There were multiple cutoff values s for antibody {hla_code_raw} '
                                 'This means inconsistency that is not allowed.')
        cutoff = cutoffs.pop()
        mfi = get_mfi_from_multiple_hla_codes([hla_code.mfi for hla_code in antibody_group_list],
                                              cutoff,
                                              hla_code_raw,
                                              logger_with_patient)
        new_antibody = HLAAntibody(
            code=antibody_group_list[0].code,
            raw_code=hla_code_raw,
            cutoff=cutoff,
            mfi=mfi
        )
        hla_antibodies_joined.append(new_antibody)

    return hla_antibodies_joined


def _filter_antibodies_over_cutoff(
        hla_antibodies: List[HLAAntibody]
) -> List[HLAAntibody]:
    return [
        hla_antibody for hla_antibody in hla_antibodies
        if hla_antibody.mfi >= hla_antibody.cutoff
    ]


HLACodeAlias = Union[HLAType, HLAAntibody]


def _is_hla_type_in_group(hla_type: HLACodeAlias, hla_group: HLAGroup) -> bool:
    if hla_type.code.broad is not None:
        return bool(re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code.broad))
    elif hla_type.code.high_res is not None:
        return bool(re.match(HLA_GROUP_HIGH_RES_CODE_REGEX[hla_group], hla_type.code.high_res))
    else:
        raise AssertionError(f'Split or high res should be provided: {hla_type.code}')


def _split_hla_types_to_groups(hla_types: List[HLACodeAlias]
                               ) -> Dict[HLAGroup, List[HLACodeAlias]]:
    hla_types_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if _is_hla_type_in_group(hla_type, hla_group):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return hla_types_in_groups
