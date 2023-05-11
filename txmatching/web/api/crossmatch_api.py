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
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.patients.hla_model import HLATypeRaw, HLAAntibodies, HLAType
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
        crossmatch_dto = request_body(CrossmatchDTOIn)

        hla_antibodies, antibodies_parsing_issues = _get_hla_antibodies_and_parsing_issues(
            crossmatch_dto.recipient_antibodies)
        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(crossmatch_dto.get_maximum_donor_hla_typing(),
                                               # TODO: https://github.com/mild-blue/txmatching/issues/1204
                                               ignore_max_number_hla_types_per_group=True),
            recipient_antibodies=hla_antibodies,
            use_high_resolution=True)

        assumed_hla_typing, typing_parsing_issues = _solve_potential_hla_typing(
            crossmatch_dto.potential_donor_hla_typing, hla_antibodies)
        antibody_matches_for_hla_type = [
            AntibodyMatchForHLAType.from_crossmatched_antibodies(
                assumed_hla_type=assumed_hla_type,
                crossmatched_antibodies=crossmatched_antibodies_per_group)
            for assumed_hla_type in assumed_hla_typing]

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antibody_matches_for_hla_type,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues
        ))


def _get_hla_antibodies_and_parsing_issues(antibodies: List[HLAAntibodiesUploadDTO]) \
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


def _solve_potential_hla_typing(potential_hla_typing_raw: List[List[str]],
                                antibodies_to_solve_hla_typing: HLAAntibodies) \
        -> Tuple[List[List[HLAType]], List[ParsingIssueBase]]:
    """
    :param potential_hla_typing_raw: has a very similar meaning to assumed
                                     (has all the same limitations, viz AntibodyMatchForHLAType),
                                     but is a more extended version. Usually, all high res codes for
                                     assumed HLA type are presented in the corresponding antibodies,
                                     or they occur just once. So we have to analyze all potential
                                     hla types against certain list of antibodies to satisfy this condition.
    :param antibodies_to_solve_hla_typing: certain antibodies which help to transform potential
                                           HLA Typing into assumed.
    :return: solved assumed HLA typing and parsing issues for the remaining assumed HLA typing.
    """
    antibodies_codes = antibodies_to_solve_hla_typing.get_antibodies_codes_as_list()
    # Solve potential HLA typing, thus we get assumed HLA typing
    assumed_hla_typing = []
    for potential_hla_type_raw in potential_hla_typing_raw:
        potential_hla_type = [create_hla_type(hla) for hla in potential_hla_type_raw]
        AntibodyMatchForHLAType.validate_assumed_hla_type(potential_hla_type)

        if len(potential_hla_type) == 1:
            # just one code -> solved
            assumed_hla_typing.append(potential_hla_type)
            continue
        # Try to leave only those HLA types that have their codes among antibodies
        maybe_assumed_hla_type = [hla_type for hla_type in potential_hla_type
                                  if hla_type.code in antibodies_codes]
        if maybe_assumed_hla_type:
            assumed_hla_typing.append(maybe_assumed_hla_type)
            continue
        # If there are none found, then it's not a problem.
        # Convert the entire potential HLA type to low resolution.
        assumed_hla_typing.append(_convert_potential_hla_type_to_low_res(potential_hla_type))

    # Get parsing issues
    assumed_hla_typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(
        HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla.raw_code) for assumed_hla_type in
                            assumed_hla_typing for hla in assumed_hla_type]
        ))

    return assumed_hla_typing, assumed_hla_typing_parsing_issues


def _convert_potential_hla_type_to_low_res(potential_hla_type: List[HLAType]) -> List[HLAType]:
    return [create_hla_type(raw_code=potential_hla_type[0].code.get_low_res_code())]
