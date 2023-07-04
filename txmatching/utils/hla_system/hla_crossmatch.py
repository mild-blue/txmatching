import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Set

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_functions import (
    analyze_if_high_res_antibodies_are_type_a, is_all_antibodies_in_high_res)
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibodies,
                                           HLAAntibody, HLAPerGroup,
                                           HLAType, HLATypeWithFrequency,
                                           HLATyping)
from txmatching.utils.enums import (AntibodyMatchTypes, HLAAntibodyType,
                                    HLACrossmatchLevel, HLAGroup)
from txmatching.utils.hla_system.rel_dna_ser_exceptions import \
    MULTIPLE_SERO_CODES_LIST

logger = logging.getLogger(__name__)

MATCHING_TYPE_ORDER = [AntibodyMatchTypes.HIGH_RES, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                       AntibodyMatchTypes.HIGH_RES_WITH_BROAD, AntibodyMatchTypes.SPLIT, AntibodyMatchTypes.BROAD,
                       AntibodyMatchTypes.UNDECIDABLE]


@dataclass(eq=True, frozen=True)
class AntibodyMatch:
    hla_antibody: HLAAntibody
    match_type: AntibodyMatchTypes


@dataclass
class AntibodyMatchForHLAGroup:
    hla_group: HLAGroup
    antibody_matches: List[AntibodyMatch]


class CadaverousCrossmatchDetailsIssues(str, Enum):
    RARE_ALLELE_POSITIVE_CROSSMATCH = 'There is most likely no crossmatch, but there is a small chance that a ' \
                                      'crossmatch could occur. Therefore, this case requires further investigation.' \
                                      'In summary we send SPLIT resolution of an infrequent code with the highest ' \
                                      'MFI value among antibodies that have rare positive ' \
                                      'crossmatch.'
    ANTIBODIES_MIGHT_NOT_BE_DSA = 'Antibodies against this HLA Type might not be DSA, for more ' \
                                  'see detailed section.'  # DSA = Donor-specific antibody
    AMBIGUITY_IN_HLA_TYPIZATION = 'Ambiguous HLA typization, multiple crossmatched frequent HLA codes with ' \
                                  'different SPLIT level.'
    NEGATIVE_ANTIBODY_IN_SUMMARY = 'There are no frequent antibodies crossmatched against this HLA type, ' \
                                   'the HLA code in summary corresponds to an antibody with mfi below cutoff and ' \
                                   'is therefore not displayed in the list of matched antibodies.'
    NO_MATCHING_ANTIBODY = 'No matching antibody was found against this HLA type, HLA code displayed in summary ' \
                           'taken from the HLA type.'
    HIGH_RES_MATCH = 'There is a single positively crossmatched HIGH RES HLA type - HIGH RES antibody pair.'
    HIGH_RES_MATCH_ON_SPLIT_LEVEL = "Recipient was not tested for donor's HIGH RES HLA type (or donor's HLA type is " \
                                    "in SPLIT resolution), but all HIGH RES antibodies corresponding to the " \
                                    "summary HLA code on SPLIT level are positively crossmatched."
    MULTIPLE_HIGH_RES_MATCH = 'SPLIT HLA code displayed in summary, but there are multiple positive crossmatches of ' \
                              'HIGH RES HLA type - HIGH RES antibody pairs.'
    HIGH_RES_WITH_SPLIT_BROAD_MATCH = 'There is no exact match, but some of the HIGH RES antibodies corresponding to' \
                                      'the summary HLA code on SPLIT or BROAD level are positive.'
    SPLIT_BROAD_MATCH = 'There is a match in SPLIT or BROAD resolution.'
    THEORETICAL_MATCH = 'There is a match with theoretical antibody.'
    NONE_MATCH = 'There is a match of type NONE, this is most probably caused by only one of the antibodies from ' \
                 'double antibody finding a match.'


@dataclass
class CrossmatchSummary:
    hla_code: HLACode
    mfi: Optional[int]
    details_and_issues: Optional[List[CadaverousCrossmatchDetailsIssues]]


@dataclass
class AntibodyMatchForHLAType:
    # If we have List[HLAType], which biologically carries the meaning of only one HLA Type
    # (we simply cannot choose which one is the right one),
    # then we call that object assumed_hla_type, and it has the following properties:
    # - must not be empty
    # - must have a uniform HLA code in low res, i.e we do not allow situation ['A*01:01', 'A*02:01']
    # - must not have several codes in low res, i.e. we do not allow situation ['A1', 'A1']
    is_crossmatch: bool
    assumed_hla_types: List[HLATypeWithFrequency]
    antibody_matches: List[AntibodyMatch] = field(default_factory=list)
    summary: Optional[CrossmatchSummary] = field(init=False)  # antibody with the largest MFI value

    def __init__(self, assumed_hla_types: List[HLATypeWithFrequency],
                 antibody_matches: List[AntibodyMatch] = None,
                 all_antibodies: List[AntibodiesPerGroup] = None):
        if not assumed_hla_types:
            raise AttributeError('AntibodyMatchForHLAType needs at least one assumed hla_type.')

        self.assumed_hla_types = assumed_hla_types
        self.antibody_matches = antibody_matches or []
        self.is_crossmatch = self.check_if_crossmatch()
        self.summary = self._calculate_crossmatch_summary(all_antibodies=all_antibodies or [])

    @classmethod
    def from_crossmatched_antibodies(cls, assumed_hla_types: List[HLATypeWithFrequency],
                                     crossmatched_antibodies: List[AntibodyMatchForHLAGroup],
                                     all_antibodies: List[AntibodiesPerGroup]):
        """
        Generates an instance of the AntibodyMatchForHLAType according to the assumed HLA type
        and possible pre-calculated crossmatched antibodies.
        :param assumed_hla_types: special representation of the classic HLAType (see comment
                                 at the begging of the dataclass AntibodyMatchForHLAType)
        :param crossmatched_antibodies: antibodies that we know are likely to have a crossmatch
                                        but are categorized into HLA groups.
        :param all_antibodies: all antibodies, categorized into HLA groups.
        :return: instance of this class.
        """
        if not assumed_hla_types:
            raise AttributeError('AntibodyMatchForHLAType needs at least one assumed hla_type.')
        antibody_matches = cls._find_common_matches(assumed_hla_types, crossmatched_antibodies)
        return cls(assumed_hla_types, antibody_matches, all_antibodies)

    def check_if_crossmatch(self):
        if len(self.antibody_matches) == 0:
            return False
        for match in self.antibody_matches:
            if match.match_type in (AntibodyMatchTypes.UNDECIDABLE, AntibodyMatchTypes.NONE):
                return False
        return True

    # pylint: disable=too-many-locals
    def _calculate_crossmatch_summary(self, all_antibodies: List[AntibodiesPerGroup]):
        frequent_codes = [
            hla_type.hla_type.code
            for hla_type in self.assumed_hla_types
            if hla_type.is_frequent
        ]

        if not self.antibody_matches:
            # Pretend all the negative antibodies are positive matches to utilise the _find_common_matches fnc
            negative_antibody_matches = []
            for antibodies_group in all_antibodies:
                frequent_negative_antibodies_group =\
                    list(filter(lambda m: m.code in frequent_codes or m.second_code in frequent_codes,
                                antibodies_group.hla_antibody_list))
                negative_antibody_matches.append(
                    AntibodyMatchForHLAGroup(
                        hla_group=antibodies_group.hla_group,
                        antibody_matches=[AntibodyMatch(hla_antibody=hla_antibody, match_type=AntibodyMatchTypes.NONE)
                                          for hla_antibody in frequent_negative_antibodies_group]
                    )
                )

            common_matches = self._find_common_matches(self.assumed_hla_types, negative_antibody_matches)

            if common_matches:
                summary_match = max(common_matches,
                                    key=lambda m: m.hla_antibody.mfi)
                return CrossmatchSummary(
                    hla_code=summary_match.hla_antibody.code.to_low_res_hla_code(),
                    mfi=summary_match.hla_antibody.mfi,
                    details_and_issues=[CadaverousCrossmatchDetailsIssues.NEGATIVE_ANTIBODY_IN_SUMMARY]
                )
            else:
                # This is a special case that can occur with codes such as `A*01:01N`. Such codes picked to be in
                # assumed hla types even without supporting antibody (consequently, there is not even a negative match
                # to be found for them here).
                # We also implicitly expect here that the assumed_hla_types is of length 1 in this case, if it is
                # larger, we only display the first code.
                return CrossmatchSummary(
                    hla_code=self.assumed_hla_types[0].hla_type.code,
                    mfi=None,
                    details_and_issues=[CadaverousCrossmatchDetailsIssues.NO_MATCHING_ANTIBODY]
                )

        matches_with_frequent_codes = list(filter(
            lambda m: m.hla_antibody.code in frequent_codes or
                      m.hla_antibody.second_code in frequent_codes,
            self.antibody_matches
        ))
        if not matches_with_frequent_codes:
            # there are not any antibody matches with frequent codes,
            # so the crossmatch is very unlikely
            summary_match = max(self.antibody_matches,
                                key=lambda m: m.hla_antibody.mfi)
            return CrossmatchSummary(
                hla_code=summary_match.hla_antibody.code.to_low_res_hla_code(),
                mfi=summary_match.hla_antibody.mfi,
                details_and_issues=[CadaverousCrossmatchDetailsIssues.RARE_ALLELE_POSITIVE_CROSSMATCH]
            )

        # get summary match type
        antibodies_matched_types = [antibody_match.match_type for antibody_match
                                    in matches_with_frequent_codes]
        summary_match_type = max(antibodies_matched_types)
        # Further we will only consider antibodies with match_type == summary_match_type
        matches_with_frequent_codes_and_summary_type = list(filter(
            lambda m: m.match_type == summary_match_type,
            matches_with_frequent_codes
        ))
        assert matches_with_frequent_codes_and_summary_type, \
            "For now, we assume that these lists have at least one element. " \
            "If not, then this is a logic error in the code."

        # get crossmatch type details and issues
        crossmatch_details_and_issues = self._calculate_crossmatch_details_and_issues(
            frequent_codes, matches_with_frequent_codes_and_summary_type)

        # get summary HLA code
        summary_hla_code = max(
            matches_with_frequent_codes_and_summary_type,
            key=lambda match: match.hla_antibody.mfi).hla_antibody.code.to_low_res_hla_code() \
            if len(matches_with_frequent_codes_and_summary_type) > 1 \
            else matches_with_frequent_codes_and_summary_type[0].hla_antibody.code

        # get summary MFI value
        antibodies_matched_mfis_for_summary_code = [
            antibody_match.hla_antibody.mfi
            for antibody_match in matches_with_frequent_codes_and_summary_type
            if antibody_match.hla_antibody.code.get_low_res_code()
               == summary_hla_code.get_low_res_code()
               or (antibody_match.hla_antibody.second_code is not None and
                   antibody_match.hla_antibody.second_code.get_low_res_code()
                   == summary_hla_code.get_low_res_code())
        ]
        summary_mfi = int(sum(antibodies_matched_mfis_for_summary_code) / len(
            antibodies_matched_mfis_for_summary_code))

        return CrossmatchSummary(
            hla_code=summary_hla_code,
            mfi=summary_mfi,
            details_and_issues=crossmatch_details_and_issues
        )

    # pylint: disable=too-many-branches
    @staticmethod
    def _calculate_crossmatch_details_and_issues(frequent_codes: List[HLACode],
                                                 matches_with_frequent_codes_and_summary_type: List[AntibodyMatch]) \
            -> List[CadaverousCrossmatchDetailsIssues]:
        crossmatch_detail_and_issues: List[CadaverousCrossmatchDetailsIssues] = []
        # Match type info (all matches are already filtered to have the same match type, we can use single match
        # to infer it)
        match_type = matches_with_frequent_codes_and_summary_type[0].match_type
        if match_type == AntibodyMatchTypes.NONE:
            crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.NONE_MATCH)
        elif match_type == AntibodyMatchTypes.THEORETICAL:
            crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.THEORETICAL_MATCH)
        elif match_type in (AntibodyMatchTypes.BROAD, AntibodyMatchTypes.SPLIT):
            crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.SPLIT_BROAD_MATCH)
        elif match_type in (AntibodyMatchTypes.HIGH_RES_WITH_BROAD, AntibodyMatchTypes.HIGH_RES_WITH_SPLIT):
            crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.HIGH_RES_WITH_SPLIT_BROAD_MATCH)
        elif match_type == AntibodyMatchTypes.HIGH_RES:
            if HLACode.are_codes_in_high_res(frequent_codes):
                if len(matches_with_frequent_codes_and_summary_type) > 1:
                    crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.MULTIPLE_HIGH_RES_MATCH)
                else:
                    # len(matches_with_frequent_codes_and_summary_type) == 1 ->
                    # -> true high res (single antibody-hla code pair)
                    crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH)
            else:
                # Everything is in split, HIGH_RES match could not have been achieved by high_res-high_res
                # corresspondence.
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.HIGH_RES_MATCH_ON_SPLIT_LEVEL)
        else:
            raise AssertionError(f"Unexpected match type: {match_type}. Such type is unknown or "
                                 f"should not occur at this point.")

        # Issues
        if not len(frequent_codes) > 1 or not HLACode.are_codes_in_high_res(frequent_codes):
            return crossmatch_detail_and_issues
        elif not HLACode.do_codes_have_different_low_res(frequent_codes):
            crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA)
            return crossmatch_detail_and_issues
        else:
            if len(frequent_codes) == len(matches_with_frequent_codes_and_summary_type):
                # all codes above cutoff
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.AMBIGUITY_IN_HLA_TYPIZATION)
                return crossmatch_detail_and_issues
            else:
                # some codes below cutoff
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.ANTIBODIES_MIGHT_NOT_BE_DSA)
                return crossmatch_detail_and_issues

    @classmethod
    def _find_common_matches(cls, assumed_hla_types: List[HLATypeWithFrequency],
                             crossmatched_antibodies: List[AntibodyMatchForHLAGroup]) \
            -> Optional[List[AntibodyMatch]]:
        return [antibody_group_match for match_per_group in crossmatched_antibodies
                for antibody_group_match in match_per_group.antibody_matches
                if cls._are_assumed_hla_types_corresponds_antibody(assumed_hla_types,
                                                                   antibody_group_match.hla_antibody)]

    @classmethod
    def _are_assumed_hla_types_corresponds_antibody(cls, assumed_hla_types: List[HLATypeWithFrequency],
                                                    hla_antibody: HLAAntibody) -> bool:
        for assumed_hla_type in assumed_hla_types:
            if assumed_hla_type.hla_type.code == hla_antibody.code or \
                    (hla_antibody.second_code and assumed_hla_type.hla_type.code == hla_antibody.second_code):
                return True
        return False

    def __hash__(self):
        return hash((tuple(self.assumed_hla_types), tuple(self.antibody_matches)))

    def __eq__(self, other):
        return hash(self) == hash(other)


def get_crossmatched_antibodies_per_group(donor_hla_typing: HLATyping,
                                          recipient_antibodies: HLAAntibodies,
                                          use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    if is_recipient_type_a(recipient_antibodies):
        antibody_matches_for_groups = do_crossmatch_in_type_a(donor_hla_typing,
                                                              recipient_antibodies,
                                                              use_high_resolution)
    else:
        antibody_matches_for_groups = do_crossmatch_in_type_b(donor_hla_typing,
                                                              recipient_antibodies,
                                                              use_high_resolution)

    # Sort antibodies
    for antibodies_per_hla_group in antibody_matches_for_groups:
        antibodies_per_hla_group.antibody_matches = sorted(
            antibodies_per_hla_group.antibody_matches,
            key=lambda hla_group: (
                hla_group.hla_antibody.raw_code,
                hla_group.hla_antibody.second_raw_code if hla_group.hla_antibody.second_raw_code is not None else '',
                hla_group.match_type
            ))

    return antibody_matches_for_groups


def is_positive_hla_crossmatch(donor_hla_typing: HLATyping,
                               recipient_antibodies: HLAAntibodies,
                               use_high_resolution: bool,
                               crossmatch_level: HLACrossmatchLevel = HLACrossmatchLevel.NONE,
                               crossmatch_logic: Callable = get_crossmatched_antibodies_per_group) -> bool:
    """
    Do donor and recipient have positive crossmatch in HLA system?
    e.g. A23 -> A23 True
         A9 -> A9  True
         A23 -> A9 True
         A23 -> A24 False if use_high_resolution else True
         A9 -> A23 True
         A9 broad <=> A23, A24 split
    :param donor_hla_typing: donor hla_typing to crossmatch
    :param recipient_antibodies: recipient antibodies to crossmatch
    :param use_high_resolution: setting whether to high res resolution for crossmatch determination
    :param crossmatch_level:
    :param crossmatch_logic:
    :return:
    """
    common_codes = {antibody_match.hla_antibody for antibody_match_group in
                    crossmatch_logic(donor_hla_typing, recipient_antibodies, use_high_resolution)
                    for antibody_match in antibody_match_group.antibody_matches
                    if antibody_match.match_type.is_positive_for_level(crossmatch_level)}
    # if there are any common codes, positive crossmatch is found
    return len(common_codes) > 0


# pylint: disable=too-many-branches
def do_crossmatch_for_selected_antibodies(hla_per_group: HLAPerGroup, antibodies_to_check: List[HLAAntibody],
                                          all_antibodies: List[HLAAntibody], use_high_resolution: bool
                                          ) -> Set[AntibodyMatch]:
    for antibody in antibodies_to_check:
        # TODO improve the code around multiple sero codes https://github.com/mild-blue/txmatching/issues/1036
        if antibody.code.high_res is None and antibody.code.split not in MULTIPLE_SERO_CODES_LIST:
            raise InvalidArgumentException(f'Crossmatch type a cannot be computed if some of'
                                           f'patient antibodies is not in high res. Antibody: '
                                           f'{antibody} does not have high res')
    positive_matches = set()
    _add_undecidable_crossmatch_type(_get_antibodies_over_cutoff(antibodies_to_check), hla_per_group, positive_matches)

    for hla_type in hla_per_group.hla_types:
        if use_high_resolution and hla_type.code.high_res is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies_to_check
                                            if hla_type.code.high_res == antibody.code.high_res]

            # HIGH_RES_1
            if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                               AntibodyMatchTypes.HIGH_RES,
                                               positive_matches):
                continue
            if not _recipient_was_tested_for_donor_antigen(antibodies_to_check, hla_type.code):
                continue

        if hla_type.code.split is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies_to_check
                                            if hla_type.code.split == antibody.code.split
                                            if hla_type.code.split is not None]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

            all_tested_antibodies_that_match = [antibody for antibody in all_antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
            all_positive_tested_antibodies = _get_antibodies_over_cutoff(all_tested_antibodies_that_match)

            # HIGH_RES_3
            if hla_type.code.high_res is None:
                if _add_all_tested_positive_antibodies(all_tested_antibodies_that_match,
                                                       all_positive_tested_antibodies,
                                                       positive_tested_antibodies,
                                                       AntibodyMatchTypes.HIGH_RES,
                                                       positive_matches):
                    continue

            # HIGH_RES_WITH_SPLIT_1
            if _add_positive_tested_antibodies(positive_tested_antibodies,
                                               AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                                               positive_matches):
                continue

            # SPLIT_1
            if hla_type.code.high_res is None:
                if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                   AntibodyMatchTypes.SPLIT,
                                                   positive_matches):
                    continue

        if hla_type.code.broad is not None:
            tested_antibodies_that_match = [antibody for antibody in antibodies_to_check
                                            if hla_type.code.broad == antibody.code.broad]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)
            all_tested_antibodies_that_match = [antibody for antibody in all_antibodies
                                                if hla_type.code.broad == antibody.code.broad]
            all_positive_tested_antibodies = _get_antibodies_over_cutoff(all_tested_antibodies_that_match)

            # HIGH_RES_3
            if hla_type.code.high_res is None:
                if _add_all_tested_positive_antibodies(all_tested_antibodies_that_match,
                                                       all_positive_tested_antibodies,
                                                       positive_tested_antibodies,
                                                       AntibodyMatchTypes.HIGH_RES,
                                                       positive_matches):
                    continue

            # HIGH_RES_WITH_BROAD_1
            if hla_type.code.high_res is None and hla_type.code.split is None:
                if _add_positive_tested_antibodies(positive_tested_antibodies,
                                                   AntibodyMatchTypes.HIGH_RES_WITH_BROAD,
                                                   positive_matches):
                    continue

            # BROAD_1
            if hla_type.code.high_res is None and hla_type.code.split is None:
                if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                   AntibodyMatchTypes.BROAD,
                                                   positive_matches):
                    continue

    return positive_matches


# pylint: disable=too-many-nested-blocks
def do_crossmatch_in_type_a(donor_hla_typing: HLATyping,
                            recipient_antibodies: HLAAntibodies,
                            use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []
    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        antibodies = antibodies_per_group.hla_antibody_list
        if hla_per_group.hla_group not in {HLAGroup.DP, HLAGroup.DQ}:
            positive_matches = do_crossmatch_for_selected_antibodies(
                hla_per_group, antibodies, antibodies, use_high_resolution)
            _do_crossmatch_for_hlas_recipient_was_not_tested_for(
                hla_per_group, antibodies, antibodies, positive_matches, use_high_resolution)
        else:
            positive_matches = set()
            for antibody in antibodies:
                # if antibody has 2 codes, both of them has to have a crossmatch, otherwise there will be none
                if antibody.second_raw_code is not None:
                    second_antibody = HLAAntibody(raw_code=antibody.second_raw_code, code=antibody.second_code,
                                                  mfi=antibody.mfi,
                                                  cutoff=antibody.cutoff)
                    positive_matches_two_antibodies = do_crossmatch_for_selected_antibodies(
                        hla_per_group, [antibody, second_antibody], antibodies, use_high_resolution)
                    _do_crossmatch_for_hlas_recipient_was_not_tested_for(
                        hla_per_group, [antibody, second_antibody], antibodies, positive_matches_two_antibodies,
                        use_high_resolution)
                    if len(positive_matches_two_antibodies) == 2:
                        lowest_match_type = _sort_match_types(
                            [positive_match.match_type for positive_match in list(positive_matches_two_antibodies)])[-1]
                        positive_matches.add(AntibodyMatch(antibody, lowest_match_type))
                else:
                    positive_matches = positive_matches.union(
                        do_crossmatch_for_selected_antibodies(hla_per_group, [antibody], antibodies,
                                                              use_high_resolution))
                    _do_crossmatch_for_hlas_recipient_was_not_tested_for(
                        hla_per_group, [antibody], antibodies, positive_matches, use_high_resolution)

        _add_theoretical_crossmatch_type(positive_matches)
        _add_none_crossmatch_type(_get_antibodies_over_cutoff(antibodies), positive_matches)
        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))
    return antibody_matches_for_groups


def _sort_match_types(match_types: List[AntibodyMatchTypes]):
    return [match_type for correct_type in MATCHING_TYPE_ORDER for match_type in match_types if
            match_type == correct_type]


def _do_crossmatch_for_hlas_recipient_was_not_tested_for(hla_per_group: HLAPerGroup,
                                                         antibodies_to_check: List[HLAAntibody],
                                                         all_antibodies: List[HLAAntibody],
                                                         positive_matches: Set[AntibodyMatch],
                                                         use_high_resolution: bool):
    # iterate over hla types and look for codes that recipient was not tested for
    for hla_type in hla_per_group.hla_types:
        if use_high_resolution and hla_type.code.high_res is not None and not _recipient_was_tested_for_donor_antigen(
                all_antibodies, hla_type.code):
            # select antibodies that match from the list of antibodies that are to check and to be added to positive matches
            tested_antibodies_that_match = [antibody for antibody in antibodies_to_check
                                            if hla_type.code.split == antibody.code.split
                                            if hla_type.code.split is not None and
                                            antibody.raw_code not in
                                            [antibody_match.hla_antibody.raw_code for antibody_match in
                                             positive_matches]]
            positive_tested_antibodies = _get_antibodies_over_cutoff(tested_antibodies_that_match)

            # find out whether all antibodies that match are over cutoff
            all_tested_antibodies_that_match = [antibody for antibody in all_antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
            all_positive_tested_antibodies = _get_antibodies_over_cutoff(all_tested_antibodies_that_match)

            # HIGH_RES_2
            if _add_all_tested_positive_antibodies(all_tested_antibodies_that_match,
                                                   all_positive_tested_antibodies,
                                                   positive_tested_antibodies,
                                                   AntibodyMatchTypes.HIGH_RES,
                                                   positive_matches):
                continue

            # HIGH_RES_WITH_SPLIT_2
            if _add_positive_tested_antibodies(positive_tested_antibodies,
                                               AntibodyMatchTypes.HIGH_RES_WITH_SPLIT,
                                               positive_matches):
                continue


def do_crossmatch_in_type_b(donor_hla_typing: HLATyping,
                            recipient_antibodies: HLAAntibodies,
                            use_high_resolution: bool) -> List[AntibodyMatchForHLAGroup]:
    antibody_matches_for_groups = []

    for hla_per_group, antibodies_per_group in zip(donor_hla_typing.hla_per_groups,
                                                   recipient_antibodies.hla_antibodies_per_groups):
        positive_matches = set()
        antibodies = antibodies_per_group.hla_antibody_list

        _add_undecidable_crossmatch_type(_get_antibodies_over_cutoff(antibodies), hla_per_group, positive_matches)

        for hla_type in hla_per_group.hla_types:
            if use_high_resolution and hla_type.code.high_res is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.high_res == antibody.code.high_res]
                # HIGH_RES_1
                if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                                   AntibodyMatchTypes.HIGH_RES,
                                                   positive_matches):
                    continue

            if hla_type.code.split is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.split == antibody.code.split
                                                if hla_type.code.split is not None]
                if _add_split_crossmatch_type(hla_type, tested_antibodies_that_match, positive_matches):
                    continue

            if hla_type.code.broad is not None:
                tested_antibodies_that_match = [antibody for antibody in antibodies
                                                if hla_type.code.broad == antibody.code.broad]
                if _add_broad_crossmatch_type(hla_type, tested_antibodies_that_match, positive_matches):
                    continue

        _add_theoretical_crossmatch_type(positive_matches)
        _add_none_crossmatch_type(antibodies, positive_matches)

        antibody_matches_for_groups.append(AntibodyMatchForHLAGroup(hla_per_group.hla_group, list(positive_matches)))

    return antibody_matches_for_groups


def is_recipient_type_a(recipient_antibodies: HLAAntibodies) -> bool:
    hla_antibodies_from_all_groups = []
    for antibodies_per_group in recipient_antibodies.hla_antibodies_per_groups:
        hla_antibodies_from_all_groups += antibodies_per_group.hla_antibody_list

    if not is_all_antibodies_in_high_res(hla_antibodies_from_all_groups):
        return False

    return analyze_if_high_res_antibodies_are_type_a(
        hla_antibodies_from_all_groups).is_type_a_compliant


def _get_antibodies_over_cutoff(antibodies: List[HLAAntibody]) -> List[HLAAntibody]:
    return [antibody for antibody in antibodies if antibody.mfi >= antibody.cutoff]


def _recipient_was_tested_for_donor_antigen(antibodies: List[HLAAntibody], antigen: HLACode) -> bool:
    return antigen in [antibody.code for antibody in antibodies]


def _add_all_tested_positive_antibodies(all_tested_antibodies_that_match: List[HLAAntibody],
                                        all_positive_tested_antibodies: List[HLAAntibody],
                                        tested_antibodies_to_add: List[HLAAntibody],
                                        match_type: AntibodyMatchTypes,
                                        positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if crossmatch has happened."""

    if len(all_positive_tested_antibodies) > 0:
        if len(all_tested_antibodies_that_match) == len(all_positive_tested_antibodies):
            for antibody in tested_antibodies_to_add:
                positive_matches.add(AntibodyMatch(antibody, match_type))
            return True
    return False


def _add_positive_tested_antibodies(tested_antibodies_that_match: List[HLAAntibody],
                                    match_type: AntibodyMatchTypes,
                                    positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if crossmatch has happened."""

    if len(tested_antibodies_that_match) > 0:
        for antibody in _get_antibodies_over_cutoff(tested_antibodies_that_match):
            positive_matches.add(AntibodyMatch(antibody, match_type))
        return True
    return False


def _add_split_crossmatch_type(hla_type: HLAType,
                               tested_antibodies_that_match: List[HLAAntibody],
                               positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if split crossmatch has happened."""

    # SPLIT_1
    if hla_type.code.high_res is None:
        if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                           AntibodyMatchTypes.SPLIT,
                                           positive_matches):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None]
    # SPLIT_2
    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                       AntibodyMatchTypes.SPLIT,
                                       positive_matches):
        return True

    return False


def _add_broad_crossmatch_type(hla_type: HLAType,
                               tested_antibodies_that_match: List[HLAAntibody],
                               positive_matches: Set[AntibodyMatch]) -> bool:
    """Return True if broad crossmatching has happened."""

    # BROAD_1
    if hla_type.code.high_res is None and hla_type.code.split is None:
        if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                           AntibodyMatchTypes.BROAD,
                                           positive_matches):
            return True

    tested_antibodies_that_match = [antibody for antibody in tested_antibodies_that_match
                                    if antibody.code.high_res is None and antibody.code.split is None]
    # BROAD_2
    if _add_positive_tested_antibodies(tested_antibodies_that_match,
                                       AntibodyMatchTypes.BROAD,
                                       positive_matches):
        return True

    return False


def _add_undecidable_crossmatch_type(antibodies: List[HLAAntibody],
                                     hla_per_group: HLAPerGroup,
                                     positive_matches: Set[AntibodyMatch]):
    if len(hla_per_group.hla_types) == 0:
        for antibody in antibodies:
            positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.UNDECIDABLE))


def _add_theoretical_crossmatch_type(positive_matches: Set[AntibodyMatch]):
    matches_to_remove = set()
    for match in positive_matches:
        if match.hla_antibody.type == HLAAntibodyType.THEORETICAL and match.match_type != AntibodyMatchTypes.UNDECIDABLE:
            matches_to_remove.add(match)
    for match in matches_to_remove:
        positive_matches.remove(match)
        positive_matches.add(AntibodyMatch(match.hla_antibody, AntibodyMatchTypes.THEORETICAL))


def _add_none_crossmatch_type(antibodies: List[HLAAntibody],
                              positive_matches: Set[AntibodyMatch]):
    antibodies_positive_matches = {match.hla_antibody for match in positive_matches}
    for antibody in _get_antibodies_over_cutoff(antibodies):
        if antibody not in antibodies_positive_matches:
            positive_matches.add(AntibodyMatch(antibody, AntibodyMatchTypes.NONE))
