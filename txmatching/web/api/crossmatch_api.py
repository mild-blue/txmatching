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
from txmatching.patients.hla_model import HLATypeRaw, HLAAntibodies
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
        antibodies_below_cutoff = hla_antibodies.get_antibodies_below_cutoff_as_list()

        antibody_matches_for_hla_type = [
            AntibodyMatchForHLAType.from_crossmatched_antibodies(
                potential_hla_type=[create_hla_type(raw_code=hla) for hla in hla_typing],
                crossmatched_antibodies=crossmatched_antibodies_per_group,
                supportive_antibodies_to_solve_potential_hla_type=antibodies_below_cutoff)
            for hla_typing in crossmatch_dto.potential_donor_hla_typing]

        typing_parsing_issues = _get_parsing_issues_for_hla_typing(antibody_matches_for_hla_type)

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


def _get_parsing_issues_for_hla_typing(antibody_matches_for_hla_type: List[AntibodyMatchForHLAType])\
        -> List[ParsingIssueBase]:
    maximum_hla_typing_raw = [hla_type.raw_code for antibody_match in antibody_matches_for_hla_type
                              for hla_type in antibody_match.assumed_hla_type]
    typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(
        HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type) for hla_type in
                            maximum_hla_typing_raw]
        ))
    return typing_parsing_issues
