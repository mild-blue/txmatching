from flask_restx import Resource

from tests.test_utilities.hla_preparation_utils import create_antibody, create_hla_type, \
    create_hla_typing
from txmatching.data_transfer_objects.crossmatch.crossmatch_dto import CrossmatchDTOIn, AntibodyMatchForHLAType, \
    CrossmatchDTOOut
from txmatching.data_transfer_objects.crossmatch.crossmatch_in_swagger import CrossmatchJsonIn, CrossmatchJsonOut
from txmatching.data_transfer_objects.patients.patient_parameters_dto import HLATypingRawDTO
from txmatching.patients.hla_model import HLATypeRaw, HLAAntibodies
from txmatching.utils.enums import HLAAntibodyType
from txmatching.utils.hla_system.hla_crossmatch import get_crossmatched_antibodies_per_group
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import \
    parse_hla_antibodies_raw_and_return_parsing_issue_list, parse_hla_typing_raw_and_return_parsing_issue_list
from txmatching.web.web_utils.namespaces import crossmatch_api
from txmatching.web.web_utils.route_utils import request_body, response_ok


@crossmatch_api.route('/do-crossmatch', methods=['POST'])
class DoCrossmatch(Resource):
    @crossmatch_api.doc(security='bearer',
                        description='Perform crossmatch test between donor HLA typing and recipient antibodies.')
    @crossmatch_api.request_body(CrossmatchJsonIn)
    @crossmatch_api.response_ok(CrossmatchJsonOut)
    @crossmatch_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @crossmatch_api.require_user_login()
    def post(self):
        crossmatch_dto = request_body(CrossmatchDTOIn)

        antibodies_raw_list = [create_antibody(antibody.name, antibody.mfi, antibody.cutoff) for antibody in
                               crossmatch_dto.recipient_antibodies]

        antibodies_parsing_issues, antibodies_dto = parse_hla_antibodies_raw_and_return_parsing_issue_list(
            antibodies_raw_list)
        typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type) for hla_type in crossmatch_dto.donor_hla_typing]
        ))

        hla_antibodies = HLAAntibodies(
            hla_antibodies_raw_list=antibodies_raw_list,
            hla_antibodies_per_groups=antibodies_dto.hla_antibodies_per_groups
        )

        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(crossmatch_dto.donor_hla_typing),
            recipient_antibodies=hla_antibodies,
            use_high_resolution=True)

        antibody_matches_for_hla_type = [AntibodyMatchForHLAType(hla_type=create_hla_type(raw_code=hla),
                                                                 antibody_matches=[])
                                            for hla in crossmatch_dto.donor_hla_typing]
        for match_per_group in crossmatched_antibodies_per_group:
            for antibody_group_match in match_per_group.antibody_matches:
                if antibody_group_match.hla_antibody.type == HLAAntibodyType.THEORETICAL or \
                        antibody_group_match.hla_antibody.second_raw_code:
                    # TODO: another TXM error with code 501
                    raise NotImplementedError('Double and theoretical antibodies are not supported yet.')
                # get AntibodyMatchForHLAType object with the same hla_type
                # as the antibody_group_match and append the antibody_group_match
                common_matches = [antibody_hla_match for antibody_hla_match in
                                  antibody_matches_for_hla_type
                                  if antibody_hla_match.hla_type.code == antibody_group_match.hla_antibody.code]
                if common_matches:
                    common_matches[0].antibody_matches.append(antibody_group_match)

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antibody_matches_for_hla_type,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues
        ))
