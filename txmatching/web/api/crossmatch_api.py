from dataclasses import dataclass
from typing import List, Tuple, Union

from flask_restx import Resource

from txmatching.auth.exceptions import TXMNotImplementedFeatureException
from txmatching.data_transfer_objects.crossmatch.crossmatch_dto import (
    AntibodyMatchForHLAType, CrossmatchDTOIn, CrossmatchDTOOut)
from txmatching.data_transfer_objects.crossmatch.crossmatch_in_swagger import (
    CrossmatchJsonIn, CrossmatchJsonOut)
from txmatching.data_transfer_objects.hla.parsing_issue_dto import \
    ParsingIssueBase
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingRawDTO
from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibodyRaw,
                                           HLATypeRaw, HLATypeWithFrequency,
                                           HLATypeWithFrequencyRaw)
from txmatching.utils.enums import HLAAntibodyType
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_antibody_matches_with_frequent_codes,
    get_crossmatched_antibodies_per_group)
from txmatching.utils.hla_system.hla_preparation_utils import (
    create_antibody, create_hla_type_with_frequency, create_hla_typing)
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import (
    HLAAntibodyPreprocessed,
    parse_hla_antibodies_raw_and_return_parsing_issue_list,
    parse_hla_raw_code_with_details,
    parse_hla_typing_raw_and_return_parsing_issue_list,
    preprocess_hla_antibodies_raw)
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.web.web_utils.namespaces import crossmatch_api
from txmatching.web.web_utils.route_utils import request_body, response_ok


@dataclass
class AssumedHLATypingParsingResult:
    assumed_hla_typing: List[List[HLATypeWithFrequency]]
    parsing_issues: List[ParsingIssueBase]

    def get_maximum_donor_hla_typing_raw(self) -> List[str]:
        return [single_assumed_hla_type.hla_type.raw_code
                for assumed_hla_type in self.assumed_hla_typing
                for single_assumed_hla_type in assumed_hla_type]


@crossmatch_api.route('/do-crossmatch', methods=['POST'])
class DoCrossmatch(Resource):
    @crossmatch_api.doc(security='bearer',
                        description='Perform crossmatch test between donor HLA typing and recipient antibodies.')
    @crossmatch_api.request_body(CrossmatchJsonIn)
    @crossmatch_api.response_ok(CrossmatchJsonOut)
    @crossmatch_api.response_errors(exceptions={TXMNotImplementedFeatureException},
                                    add_default_namespace_errors=True)
    def post(self):
        crossmatch_dto = request_body(CrossmatchDTOIn)

        antibodies_raw_list = [create_antibody(antibody.name,
                                               antibody.mfi,
                                               antibody.cutoff)
                               for antibody in crossmatch_dto.recipient_antibodies]
        hla_antibodies, antibodies_parsing_issues = _get_hla_antibodies_and_parsing_issues(
            antibodies_raw_list)

        assumed_hla_typing_parsing_result = _get_assumed_hla_typing_and_parsing_issues(
            crossmatch_dto.potential_donor_hla_typing, hla_antibodies)

        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(
                assumed_hla_typing_parsing_result.get_maximum_donor_hla_typing_raw(),
                # TODO: https://github.com/mild-blue/txmatching/issues/1204
                ignore_max_number_hla_types_per_group=True),
            recipient_antibodies=hla_antibodies,
            use_high_resolution=True)
        # Remove some antibody matches as exclusion.
        # For this endpoint, double antibodies under cutoff,
        # in which both chains are present in the donor's HLA typing, do not have a crossmatch.
        _remove_exclusive_theoretical_antibodies(
            crossmatched_antibodies_per_group,
            antibodies_raw_list,
            assumed_hla_typing_parsing_result.get_maximum_donor_hla_typing_raw())

        assumed_hla_typing = assumed_hla_typing_parsing_result.assumed_hla_typing
        typing_parsing_issues = assumed_hla_typing_parsing_result.parsing_issues

        antibody_matches_for_hla_type = [
            AntibodyMatchForHLAType.from_crossmatched_antibodies(
                assumed_hla_types=assumed_hla_type,
                crossmatched_antibodies=crossmatched_antibodies_per_group)
            for assumed_hla_type in assumed_hla_typing]

        low_frequency_parsing_issues = _get_parsing_issues_for_unlikely_crossmatches(antibody_matches_for_hla_type)

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antibody_matches_for_hla_type,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues + low_frequency_parsing_issues
        ))


def _are_all_codes_infrequent(hla_type_list: Union[List[HLATypeWithFrequencyRaw], List[HLATypeWithFrequency]]) -> bool:
    for hla_type in hla_type_list:
        if hla_type.is_frequent:
            return False
    return True


def _get_parsing_issues_for_unlikely_crossmatches(antibody_matches_for_hla_type: List[AntibodyMatchForHLAType]) -> \
        List[ParsingIssueBase]:
    parsing_issues = []
    for antibody_match in antibody_matches_for_hla_type:
        antibody_matches_with_frequent_codes = get_antibody_matches_with_frequent_codes(
            antibody_match.assumed_hla_types, antibody_match.antibody_matches)
        if len(antibody_match.antibody_matches) > 0 and \
                len(antibody_matches_with_frequent_codes) == 0:
            hla_codes = ', '.join([hla_code.hla_type.display_code
                                   for hla_code in antibody_match.assumed_hla_types])
            parsing_issues.append(ParsingIssueBase(
                hla_code_or_group=hla_codes,
                parsing_issue_detail=ParsingIssueDetail.RARE_ALLELE_POSITIVE_CROSSMATCH,
                message=ParsingIssueDetail.RARE_ALLELE_POSITIVE_CROSSMATCH.value))

    return parsing_issues


def _get_hla_antibodies_and_parsing_issues(antibodies_raw_list: List[HLAAntibodyRaw]) \
        -> Tuple[HLAAntibodies, List[ParsingIssueBase]]:
    parsing_issues, antibodies_dto = parse_hla_antibodies_raw_and_return_parsing_issue_list(
        antibodies_raw_list)
    return HLAAntibodies(
        hla_antibodies_raw_list=antibodies_raw_list,
        hla_antibodies_per_groups=antibodies_dto.hla_antibodies_per_groups), parsing_issues


def _remove_exclusive_theoretical_antibodies(crossmatched_antibodies: List[AntibodyMatchForHLAGroup],
                                             antibodies_raw: List[HLAAntibodyRaw],
                                             maximum_hla_typing_raw: List[str]):
    """
    Removes some antibody matches as exclusion. For this endpoint, double antibodies under cutoff,
    in which both chains are present in the donor's HLA typing, do not have a crossmatch.
    """
    preprocessed_hla_types_raw = list(map(_preprocess_hla_raw_code, maximum_hla_typing_raw))
    exclusive_raw_codes = _get_double_antibodies_chains_totally_represented_in_typing(
        antibodies_raw, preprocessed_hla_types_raw)
    for match_per_group in crossmatched_antibodies:
        for antibody_group_match in match_per_group.antibody_matches:
            antibody = antibody_group_match.hla_antibody
            if not antibody.type == HLAAntibodyType.THEORETICAL \
                    or antibody.raw_code not in exclusive_raw_codes:
                continue
            # delete antibody_group_match as exclusive
            del match_per_group.antibody_matches[
                match_per_group.antibody_matches.index(antibody_group_match)]


def _preprocess_hla_raw_code(hla_raw_code: str) -> str:
    maybe_high_res_code = parse_hla_raw_code_with_details(hla_raw_code).maybe_hla_code
    return maybe_high_res_code.display_code if maybe_high_res_code is not None else hla_raw_code


def _preprocess_antibodies_raw(antibodies_raw: List[HLAAntibodyRaw]) -> List[HLAAntibodyPreprocessed]:
    for antibody_raw in antibodies_raw:
        antibody_raw.raw_code = _preprocess_hla_raw_code(antibody_raw.raw_code)
    return preprocess_hla_antibodies_raw(antibodies_raw)


def _get_double_antibodies_chains_totally_represented_in_typing(antibodies_raw: List[HLAAntibodyRaw],
                                                                hla_types_raw_codes: List[str]) \
        -> List[str]:
    preprocessed_antibodies = _preprocess_antibodies_raw(antibodies_raw)
    exclusive_codes = []
    for antibody_raw_preprocessed in preprocessed_antibodies:
        if antibody_raw_preprocessed.mfi < antibody_raw_preprocessed.cutoff \
                and antibody_raw_preprocessed.raw_code in hla_types_raw_codes \
                and antibody_raw_preprocessed.secondary_raw_code in hla_types_raw_codes:
            exclusive_codes.extend([antibody_raw_preprocessed.raw_code,
                                    antibody_raw_preprocessed.secondary_raw_code])
    return exclusive_codes


def _get_assumed_hla_typing_and_parsing_issues(potential_hla_typing_raw: List[List[HLATypeWithFrequencyRaw]],
                                               supportive_antibodies: HLAAntibodies) \
        -> AssumedHLATypingParsingResult:
    """
    :param potential_hla_typing_raw: all potential hla_typing codes that were derived from
                                     a lab test (likely PCR) of patient are stored.
                                     This is then processed to assumed hla_typing that contains only
                                     the typing that has a match with antibodies and therefore is
                                     meaning for crossmatch computation.
    :param supportive_antibodies: certain antibodies which help to transform potential
                                           HLA Typing into assumed.
    :return: assumed HLA typing and parsing issues for the remaining assumed HLA typing.
    """
    antibodies_codes = supportive_antibodies.get_antibodies_codes_as_list()
    # Transform potential HLA typing into assumed HLA typing
    assumed_hla_typing = []
    for potential_hla_types_raw in potential_hla_typing_raw:
        potential_hla_types = [create_hla_type_with_frequency(hla) for hla in potential_hla_types_raw]
        AntibodyMatchForHLAType.validate_assumed_hla_types(potential_hla_types)

        # if all codes are infrequent we take only split
        if _are_all_codes_infrequent(potential_hla_types_raw):
            assumed_hla_typing.append(_convert_potential_hla_types_to_low_res(potential_hla_types))
            continue

        if len(potential_hla_types) == 1:
            # just one code -> solved
            assumed_hla_typing.append(potential_hla_types)
            continue

        # Try to leave only those HLA types that have their codes among antibodies
        maybe_assumed_hla_types = [assumed_hla_type for assumed_hla_type in potential_hla_types
                                   if assumed_hla_type.hla_type.code in antibodies_codes]

        if maybe_assumed_hla_types:
            assumed_hla_typing.append(maybe_assumed_hla_types)
            continue

        # If there are none found, then it's not a problem.
        # Convert the entire potential HLA type to low resolution.
        assumed_hla_typing.append(_convert_potential_hla_types_to_low_res(potential_hla_types))

    # Get parsing issues
    assumed_hla_typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(
        HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(assumed_hla_type.hla_type.raw_code) for assumed_hla_types in
                            assumed_hla_typing for assumed_hla_type in assumed_hla_types]
        ),
        ignore_max_number_hla_types=True)  # TODO: https://github.com/mild-blue/txmatching/issues/1204

    return AssumedHLATypingParsingResult(assumed_hla_typing,
                                         assumed_hla_typing_parsing_issues)


def _convert_potential_hla_types_to_low_res(
        potential_hla_types: List[HLATypeWithFrequency]) -> List[HLATypeWithFrequency]:
    assumed_hla_type_raw = HLATypeWithFrequencyRaw(
        hla_code=potential_hla_types[0].hla_type.code.get_low_res_code(),
        is_frequent=True
    )
    return [create_hla_type_with_frequency(assumed_hla_type_raw)]
