from typing import List, Tuple

from flask_restx import Resource

from txmatching.auth.exceptions import TXMNotImplementedFeatureException
from txmatching.data_transfer_objects.crossmatch.crossmatch_dto import CrossmatchDTOIn, \
    AntibodyMatchForHLAType, \
    CrossmatchDTOOut
from txmatching.data_transfer_objects.crossmatch.crossmatch_in_swagger import CrossmatchJsonIn, \
    CrossmatchJsonOut
from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssueBase
from txmatching.data_transfer_objects.patients.patient_parameters_dto import HLATypingRawDTO
from txmatching.patients.hla_model import HLATypeRaw, HLAAntibodies, HLAType, HLAAntibody
from txmatching.utils.hla_system.hla_crossmatch import get_crossmatched_antibodies_per_group
from txmatching.utils.hla_system.hla_preparation_utils import create_hla_typing, create_hla_type, \
    create_antibody
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import \
    parse_hla_antibodies_raw_and_return_parsing_issue_list, \
    parse_hla_typing_raw_and_return_parsing_issue_list
from txmatching.web.web_utils.namespaces import crossmatch_api
from txmatching.web.web_utils.route_utils import request_body, response_ok


@crossmatch_api.route('/do-crossmatch', methods=['POST'])
class DoCrossmatch(Resource):
    @crossmatch_api.doc(security='bearer',
                        description='Perform crossmatch test between donor HLA typing and recipient antibodies.')
    @crossmatch_api.request_body(CrossmatchJsonIn)
    @crossmatch_api.response_ok(CrossmatchJsonOut)
    @crossmatch_api.response_errors(exceptions={TXMNotImplementedFeatureException},
                                    add_default_namespace_errors=True)
    @crossmatch_api.require_user_login()
    def post(self):

        def get_hla_antibodies_and_parsing_issues(antibodies) \
                -> Tuple[HLAAntibodies, List[ParsingIssueBase]]:
            antibodies_raw_list = [create_antibody(antibody.name,
                                                   antibody.mfi,
                                                   antibody.cutoff)
                                   for antibody in antibodies]
            parsing_issues, antibodies_dto = parse_hla_antibodies_raw_and_return_parsing_issue_list(
                antibodies_raw_list)
            return HLAAntibodies(
                hla_antibodies_raw_list=antibodies_raw_list,
                hla_antibodies_per_groups=antibodies_dto.hla_antibodies_per_groups), parsing_issues

        def get_parsing_issues_for_hla_typing(antibody_matches_for_hla_type):
            maximum_hla_typing_raw = [hla_type.raw_code for antibody_match in antibody_matches_for_hla_type
                                         for hla_type in antibody_match.hla_type]
            typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(
                HLATypingRawDTO(
                    hla_types_list=[HLATypeRaw(hla_type) for hla_type in
                                    maximum_hla_typing_raw]
                ))
            return typing_parsing_issues

        def get_unique_from_list(lst: list):
            return list(dict.fromkeys(lst).keys())

        crossmatch_dto = request_body(CrossmatchDTOIn)
        hla_antibodies, antibodies_parsing_issues = get_hla_antibodies_and_parsing_issues(
            crossmatch_dto.recipient_antibodies)

        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(crossmatch_dto.get_maximum_donor_hla_typing()),
            recipient_antibodies=hla_antibodies,
            use_high_resolution=True)
        antibody_matches_for_hla_type = [AntibodyMatchForHLAType(
            hla_type=[create_hla_type(raw_code=hla) for hla in hla_typing],
            antibody_matches=[]) for hla_typing in crossmatch_dto.assumed_donor_hla_typing]

        self.__fulfill_with_common_matches(antibody_matches_for_hla_type,
                                    crossmatched_antibodies_per_group)

        antibody_matches_for_hla_type = get_unique_from_list(antibody_matches_for_hla_type)
        antibody_matches_for_hla_type = self.__solve_uncrossmatched_assumed_hla_types(
            antibody_matches_for_hla_type, hla_antibodies)

        typing_parsing_issues = get_parsing_issues_for_hla_typing(antibody_matches_for_hla_type)

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antibody_matches_for_hla_type,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues
        ))

    @staticmethod
    def __fulfill_with_common_matches(antibody_matches, crossmatched_antibodies):

        def get_hla_types_correspond_antibody(assumed_hla_type: List[HLAType],
                                              hla_antibody: HLAAntibody) -> List[HLAType]:
            return [hla_type for hla_type in assumed_hla_type
                    if hla_type.code == hla_antibody.code or
                    (hla_antibody.second_raw_code and hla_type.code == hla_antibody.second_code)]

        for antibody_hla_match in antibody_matches:
            solved_hla_types = set()
            for match_per_group in crossmatched_antibodies:
                for antibody_group_match in match_per_group.antibody_matches:
                    common_matched_hla_types: List[HLAType] = get_hla_types_correspond_antibody(
                        antibody_hla_match.hla_type, antibody_group_match.hla_antibody
                    )
                    if common_matched_hla_types:
                        solved_hla_types.update(common_matched_hla_types)
                        antibody_hla_match.antibody_matches.append(antibody_group_match)
            if solved_hla_types:
                antibody_hla_match.hla_type = list(solved_hla_types)

    def __solve_uncrossmatched_assumed_hla_types(self, antibody_matches, hla_antibodies):

        def distribute_antibody_matches_solved_unsolved(matches):
            solved_antibody_matches = []
            unsolved_antibody_matches = []
            for antibody_match in matches:
                if not antibody_match.antibody_matches and antibody_match.is_hla_type_assumed():
                    unsolved_antibody_matches.append(
                        antibody_match.get_copy_with_converted_assumed_to_low_res())
                else:
                    solved_antibody_matches.append(antibody_match)
            return solved_antibody_matches, unsolved_antibody_matches

        solved_antibody_matches, unsolved_assumed_antibody_matches = \
            distribute_antibody_matches_solved_unsolved(antibody_matches)
        crossmatched_antibodies_for_unsolved = \
            get_crossmatched_antibodies_per_group(
                donor_hla_typing=create_hla_typing([match.get_low_res_code_from_assumed()
                                                    for match in unsolved_assumed_antibody_matches]),
                recipient_antibodies=hla_antibodies,
                use_high_resolution=True
            )
        self.__fulfill_with_common_matches(unsolved_assumed_antibody_matches,
                                    crossmatched_antibodies_for_unsolved)

        solved_antibody_matches.extend(unsolved_assumed_antibody_matches)
        return solved_antibody_matches
