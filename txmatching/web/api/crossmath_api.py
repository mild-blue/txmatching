from flask_restx import Resource

from tests.test_utilities.hla_preparation_utils import create_antibody, create_hla_typing, create_antibodies
from txmatching.data_transfer_objects.crossmatch.crossmatch_dto import CrossmatchDTOIn, AntibodyMatchForHLACode, \
    CrossmatchDTOOut
from txmatching.data_transfer_objects.crossmatch.crossmatch_swagger import CrossmatchJsonIn, CrossmatchJsonOut
from txmatching.patients.hla_model import HLATypeRaw
from txmatching.utils.hla_system.hla_crossmatch import get_crossmatched_antibodies_per_group
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import \
    parse_hla_antibodies_raw_and_return_parsing_issue_list, parse_hla_typing_raw_and_return_parsing_issue_list
from txmatching.web.web_utils.namespaces import crossmatch_api
from txmatching.web.web_utils.route_utils import request_body, response_ok


@crossmatch_api.route('/do-crossmatch', methods=['POST'])
class DoCrossmatch(Resource):
    @crossmatch_api.doc(security='bearer',
                        description='Perform crossmatch between donor HLA typing and recipient antibodies.')
    @crossmatch_api.request_body(CrossmatchJsonIn)
    @crossmatch_api.response_ok(CrossmatchJsonOut)
    @crossmatch_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @crossmatch_api.require_user_login()
    def post(self):
        crossmatch_dto = request_body(CrossmatchDTOIn)

        antibodies_list = [create_antibody(antibody.name, antibody.mfi, antibody.cutoff) for antibody in
                           crossmatch_dto.recipient_antibodies]

        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(crossmatch_dto.donor_hla_typing),
            recipient_antibodies=create_antibodies(antibodies_list),
            use_high_resolution=True)

        antibodies_parsing_issues, _ = parse_hla_antibodies_raw_and_return_parsing_issue_list(
            antibodies_list)
        typing_parsing_issues, _ = parse_hla_typing_raw_and_return_parsing_issue_list(HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type) for hla_type in crossmatch_dto.donor_hla_typing]
        ))

        antigen_to_antibody = [AntibodyMatchForHLACode(hla_code=hla, antibody_matches=[]) for hla in
                               crossmatch_dto.donor_hla_typing]
        for match_per_group in crossmatched_antibodies_per_group:
            for match in match_per_group.antibody_matches:
                # get AntibodyMatchForHLACode object with the same hla_code as the match and append the match
                matched_hla = [hla for hla in antigen_to_antibody if hla.hla_code == match.hla_antibody.raw_code]
                if matched_hla:
                    matched_hla[0].antibody_matches.append(match)

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antigen_to_antibody,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues
        ))
