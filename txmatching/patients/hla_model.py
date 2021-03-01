import itertools
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Union

from txmatching.utils.enums import (HLA_GROUP_SPLIT_CODE_REGEX,
                                    HLA_GROUPS_NAMES_WITH_OTHER, HLAGroup)
from txmatching.utils.hla_system.hla_transformations import (
    get_mfi_from_multiple_hla_codes, parse_hla_raw_code)
from txmatching.utils.logging_tools import PatientAdapter
from txmatching.utils.persistent_hash import (HashType, PersistentlyHashable,
                                              update_persistent_hash)


@dataclass
class HLAType(PersistentlyHashable):
    raw_code: str
    code: str

    def __init__(self, raw_code: str, code: str = None):
        # The only places where the init is called without code specified should be
        # tests and data initialization
        self.raw_code = raw_code
        self.code = code if code is not None else parse_hla_raw_code(raw_code)

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
    hla_types_list: List[HLAType]
    hla_types_raw_list: List[HLATypeRaw]
    hla_per_groups: List[HLAPerGroup]

    def __init__(
            self,
            hla_types_list: List[HLAType],
            hla_types_raw_list: List[HLATypeRaw] = None,
            hla_per_groups: List[HLAPerGroup] = None
    ):
        # The only places where the init is called without all parameters should be tests
        self.hla_types_list = hla_types_list

        if hla_types_raw_list is None:
            hla_types_raw_list = [HLATypeRaw(hla_type.raw_code) for hla_type in hla_types_list]
        self.hla_types_raw_list = sorted(
            hla_types_raw_list,
            key=lambda hla_type_raw: hla_type_raw.raw_code.upper()
        )

        if hla_per_groups is None:
            hla_per_groups = split_hla_types_to_groups(hla_types_list)
        self.hla_per_groups = hla_per_groups

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLATyping)
        update_persistent_hash(hash_, self.hla_per_groups)


@dataclass
class HLAAntibody(PersistentlyHashable):
    raw_code: str
    mfi: int
    cutoff: int
    code: str

    def __init__(self, raw_code: str, mfi: int, cutoff: int, code: str = None):
        # The only places where the init is called without code specified should be
        # tests and data initialization
        self.raw_code = raw_code
        self.mfi = mfi
        self.cutoff = cutoff
        self.code = code if code is not None else parse_hla_raw_code(raw_code)

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
    hla_antibodies_list: List[HLAAntibody]
    hla_antibodies_raw_list: List[HLAAntibodyRaw]
    hla_antibodies_per_groups: List[AntibodiesPerGroup]

    def __init__(
            self,
            hla_antibodies_list: List[HLAAntibody],
            hla_antibodies_raw_list: List[HLAAntibodyRaw] = None,
            hla_antibodies_per_groups: List[AntibodiesPerGroup] = None
    ):
        if hla_antibodies_list is None:
            hla_antibodies_list = []
        self.hla_antibodies_list = hla_antibodies_list

        # The only places where the init is called without all parameters should be tests
        if hla_antibodies_raw_list is None:
            hla_antibodies_raw_list = [
                HLAAntibodyRaw(
                    raw_code=hla_antibody.raw_code,
                    mfi=hla_antibody.mfi,
                    cutoff=hla_antibody.cutoff
                )
                for hla_antibody in hla_antibodies_list
            ]
        self.hla_antibodies_raw_list = sorted(
            hla_antibodies_raw_list,
            key=lambda hla_antibody_raw: (hla_antibody_raw.raw_code.upper(), hla_antibody_raw.mfi)
        )

        if hla_antibodies_per_groups is None:
            # We do not set logger because computing hla_antibodies_per_groups is done here only in tests
            hla_antibodies_per_groups = create_hla_antibodies_per_groups_from_hla_antibodies(hla_antibodies_list)

        self.hla_antibodies_per_groups = hla_antibodies_per_groups

    def update_persistent_hash(self, hash_: HashType):
        update_persistent_hash(hash_, HLAAntibodies)
        update_persistent_hash(hash_, self.hla_antibodies_per_groups)


def split_hla_types_to_groups(hla_types: List[HLAType]) -> List[HLAPerGroup]:
    hla_types_in_groups = _split_hla_codes_to_groups(hla_types)
    return [HLAPerGroup(hla_group,
                        sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                        ) for hla_group, hla_codes_in_group in
            hla_types_in_groups.items()]


def create_hla_antibodies_per_groups_from_hla_antibodies(
        hla_antibodies: List[HLAAntibody],
        logger_with_patient: Union[logging.Logger, PatientAdapter] = logging.getLogger(__name__)
) -> List[AntibodiesPerGroup]:
    hla_antibodies_over_cutoff_list = _filter_antibodies_over_cutoff(hla_antibodies, logger_with_patient)
    hla_antibodies_per_groups = _split_antibodies_to_groups(hla_antibodies_over_cutoff_list)
    return hla_antibodies_per_groups


def _split_antibodies_to_groups(hla_antibodies: List[HLAAntibody]) -> List[AntibodiesPerGroup]:
    hla_antibodies_in_groups = _split_hla_codes_to_groups(hla_antibodies)
    return [AntibodiesPerGroup(hla_group,
                               sorted(hla_codes_in_group, key=lambda hla_code: hla_code.raw_code)
                               ) for hla_group, hla_codes_in_group in
            hla_antibodies_in_groups.items()]


def _filter_antibodies_over_cutoff(
        hla_antibodies: List[HLAAntibody],
        logger_with_patient: Union[logging.Logger, PatientAdapter]
) -> List[HLAAntibody]:
    def _group_key(hla_antibody: HLAAntibody) -> str:
        return hla_antibody.raw_code

    grouped_hla_antibodies = itertools.groupby(sorted(hla_antibodies, key=_group_key),
                                               key=_group_key)
    hla_antibodies_over_cutoff = []
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
        if mfi >= cutoff:
            new_antibody = HLAAntibody(
                code=antibody_group_list[0].code,
                raw_code=hla_code_raw,
                cutoff=cutoff,
                mfi=mfi
            )
            hla_antibodies_over_cutoff.append(new_antibody)

    return hla_antibodies_over_cutoff


HLACodeAlias = Union[HLAType, HLAAntibody]


def _split_hla_codes_to_groups(hla_types: List[HLACodeAlias]
                               ) -> Dict[HLAGroup, List[HLACodeAlias]]:
    hla_types_in_groups = dict()
    for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
        hla_types_in_groups[hla_group] = []
    for hla_type in hla_types:
        match_found = False
        for hla_group in HLA_GROUPS_NAMES_WITH_OTHER:
            if re.match(HLA_GROUP_SPLIT_CODE_REGEX[hla_group], hla_type.code):
                hla_types_in_groups[hla_group].append(hla_type)
                match_found = True
                break
        if not match_found:
            raise AssertionError(f'Unexpected hla_code: {hla_type.code}')
    return hla_types_in_groups
