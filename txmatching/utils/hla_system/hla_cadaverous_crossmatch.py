import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import (AntibodiesPerGroup, HLAAntibody, HLATypeWithFrequency)
from txmatching.utils.enums import AntibodyMatchTypes
from txmatching.utils.hla_system.hla_crossmatch import AntibodyMatch, AntibodyMatchForHLAGroup

logger = logging.getLogger(__name__)


class CadaverousCrossmatchDetailsIssues(str, Enum):
    # There is most likely no crossmatch, but there is a small chance that a crossmatch could occur. Therefore, this
    # case requires further investigation. In summary, we send SPLIT resolution of an infrequent code with the highest
    # MFI value among antibodies that have rare positive crossmatch.
    RARE_ALLELE_POSITIVE_CROSSMATCH = 'RARE_ALLELE_POSITIVE_CROSSMATCH'

    # Antibodies against this HLA Type might not be DSA, for more see detailed section. (DSA = Donor-specific antibody)
    ANTIBODIES_MIGHT_NOT_BE_DSA = 'ANTIBODIES_MIGHT_NOT_BE_DSA'

    # Ambiguous HLA typization, multiple crossmatched frequent HLA codes with different SPLIT level.
    AMBIGUITY_IN_HLA_TYPIZATION = 'AMBIGUITY_IN_HLA_TYPIZATION'

    # There are no frequent antibodies crossmatched against this HLA type, the HLA code in summary corresponds to an
    # antibody with mfi below cutoff and is therefore not displayed in the list of matched antibodies.
    NEGATIVE_ANTIBODY_IN_SUMMARY = 'NEGATIVE_ANTIBODY_IN_SUMMARY'

    # No matching antibody was found against this HLA type, HLA code displayed in summary taken from the HLA type.
    NO_MATCHING_ANTIBODY = 'NO_MATCHING_ANTIBODY'

    # There is a single positively crossmatched HIGH RES HLA type - HIGH RES antibody pair.
    HIGH_RES_MATCH = 'HIGH_RES_MATCH'

    # Recipient was not tested for donor's HIGH RES HLA type (or donor's HLA type is in SPLIT resolution), but all
    # HIGH RES antibodies corresponding to the summary HLA code on SPLIT level are positively crossmatched.
    HIGH_RES_MATCH_ON_SPLIT_LEVEL = 'HIGH_RES_MATCH_ON_SPLIT_LEVEL'

    # SPLIT HLA code displayed in summary, but there are multiple positive crossmatches of HIGH RES HLA type - HIGH RES
    # antibody pairs.
    MULTIPLE_HIGH_RES_MATCH = 'MULTIPLE_HIGH_RES_MATCH'

    # There is no exact match, but some of the HIGH RES antibodies corresponding to the summary HLA code on SPLIT or
    # BROAD level are positive.
    HIGH_RES_WITH_SPLIT_BROAD_MATCH = 'HIGH_RES_WITH_SPLIT_BROAD_MATCH'

    # There is a match in SPLIT or BROAD resolution.
    SPLIT_BROAD_MATCH = 'SPLIT_BROAD_MATCH'

    # There is a match with theoretical antibody.
    THEORETICAL_MATCH = 'THEORETICAL_MATCH'

    #  There is a match of type NONE, this is most probably caused by only one of the antibodies from double antibody
    #  finding a match.
    NONE_MATCH = 'NONE_MATCH'


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
    # - must have a uniform HLA code in low res, i.e. we do not allow situation ['A*01:01', 'A*02:01']
    # - must not have several codes in low res, i.e. we do not allow situation ['A1', 'A1']
    is_positive_crossmatch: bool
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
        self.is_positive_crossmatch = self.check_is_positive_crossmatch()
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

    def check_is_positive_crossmatch(self) -> bool:
        if len(self.antibody_matches) == 0:
            return False
        for match in self.antibody_matches:
            # TODO: https://github.com/mild-blue/txmatching/issues/1243 - is UNDECIDABLE positive crossmatch?
            if match.match_type in (AntibodyMatchTypes.UNDECIDABLE, AntibodyMatchTypes.NONE):
                return False
        return True

    def _calculate_crossmatch_summary(self, all_antibodies: List[AntibodiesPerGroup]):
        frequent_codes = [
            hla_type.hla_type.code
            for hla_type in self.assumed_hla_types
            if hla_type.is_frequent
        ]

        if not self.antibody_matches:
            return self._calculate_crossmatch_summary_no_positive_matches(all_antibodies, frequent_codes)
        else:
            return self._calculate_crossmatch_summary_positive_matches(frequent_codes)

    def _calculate_crossmatch_summary_no_positive_matches(self, all_antibodies, frequent_codes):
        # Pretend all the negative antibodies are positive matches to utilise the _find_common_matches fnc
        negative_antibody_matches = []
        for antibodies_group in all_antibodies:
            frequent_negative_antibodies_group = \
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

    def _calculate_crossmatch_summary_positive_matches(self, frequent_codes):
        matches_with_frequent_codes = list(filter(
            lambda m: m.hla_antibody.code in frequent_codes or m.hla_antibody.second_code in frequent_codes,
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
            if antibody_match.hla_antibody.code.get_low_res_code() == summary_hla_code.get_low_res_code()
            or (antibody_match.hla_antibody.second_code is not None
                and antibody_match.hla_antibody.second_code.get_low_res_code() == summary_hla_code.get_low_res_code())
        ]
        summary_mfi = int(sum(antibodies_matched_mfis_for_summary_code) / len(
            antibodies_matched_mfis_for_summary_code))

        return CrossmatchSummary(
            hla_code=summary_hla_code,
            mfi=summary_mfi,
            details_and_issues=crossmatch_details_and_issues
        )

    @staticmethod
    def _calculate_crossmatch_details_and_issues(frequent_codes: List[HLACode],
                                                 matches_with_frequent_codes_and_summary_type: List[AntibodyMatch]) \
            -> List[CadaverousCrossmatchDetailsIssues]:
        crossmatch_detail_and_issues: List[CadaverousCrossmatchDetailsIssues] = []
        # Match type info (all matches are already filtered to have the same match type, we can use single match
        # to infer it)
        match_type = matches_with_frequent_codes_and_summary_type[0].match_type
        match match_type:
            case AntibodyMatchTypes.NONE:
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.NONE_MATCH)
            case AntibodyMatchTypes.THEORETICAL:
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.THEORETICAL_MATCH)
            case AntibodyMatchTypes.BROAD | AntibodyMatchTypes.SPLIT:
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.SPLIT_BROAD_MATCH)
            case AntibodyMatchTypes.HIGH_RES_WITH_BROAD | AntibodyMatchTypes.HIGH_RES_WITH_SPLIT:
                crossmatch_detail_and_issues.append(CadaverousCrossmatchDetailsIssues.HIGH_RES_WITH_SPLIT_BROAD_MATCH)
            case AntibodyMatchTypes.HIGH_RES:
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
            case _:
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
