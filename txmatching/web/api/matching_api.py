# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import dataclasses
import logging

from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.data_types import UserRole
from txmatching.auth.request_context import get_user_role
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigurationJson
from txmatching.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.matchings.matching_swagger import \
    MatchingJson
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import configuration_from_dict
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from txmatching.database.services.txm_event_service import \
    get_txm_event_id_for_current_user
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLATypes, HLA_TYPE_OTHER
from txmatching.utils.matching import calculate_antigen_score, get_count_of_transplants, get_filtered_antigens, \
    get_other_antigens, get_filtered_antibodies, get_other_antibodies
from txmatching.web.api.namespaces import matching_api

logger = logging.getLogger(__name__)


@matching_api.route('/calculate-for-config', methods=['POST'])
class CalculateFromConfig(Resource):
    @matching_api.doc(body=ConfigurationJson, security='bearer')
    @matching_api.response(200, model=[MatchingJson], description='List of all matchings for given configuration.')
    @matching_api.response(code=400, model=FailJson, description='Wrong data format.')
    @matching_api.response(code=401, model=FailJson, description='Authentication failed.')
    @matching_api.response(
        code=403,
        model=FailJson,
        description='Access denied. You do not have rights to access this endpoint.'
    )
    @matching_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def post(self) -> str:
        txm_event_id = get_txm_event_id_for_current_user()
        configuration = configuration_from_dict(request.json)
        pairing_result = solve_from_configuration(configuration, txm_event_db_id=txm_event_id)
        solver_service.save_pairing_result(pairing_result)
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix(txm_event_id)

        matching_dtos = [
            dataclasses.asdict(MatchingDTO(
                rounds=[
                    RoundDTO(
                        transplants=[
                            TransplantDTOOut(
                                score=score_dict[(pair.donor.db_id, pair.recipient.db_id)],
                                compatible_blood=compatible_blood_dict[(pair.donor.db_id, pair.recipient.db_id)],
                                donor=pair.donor.medical_id,
                                recipient=pair.recipient.medical_id,
                                donor_antigens={
                                    HLATypes.A.value: get_filtered_antigens(
                                        pair.donor.parameters.hla_typing.hla_types_list,
                                        HLATypes.A.value),
                                    HLATypes.B.value: get_filtered_antigens(
                                        pair.donor.parameters.hla_typing.hla_types_list,
                                        HLATypes.B.value),
                                    HLATypes.DR.value: get_filtered_antigens(
                                        pair.donor.parameters.hla_typing.hla_types_list,
                                        HLATypes.DR.value),
                                    HLA_TYPE_OTHER: get_other_antigens(pair.donor.parameters.hla_typing.hla_types_list)
                                },
                                recipient_antigens={
                                    HLATypes.A.value: get_filtered_antigens(
                                        pair.recipient.parameters.hla_typing.hla_types_list,
                                        HLATypes.A.value),
                                    HLATypes.B.value: get_filtered_antigens(
                                        pair.recipient.parameters.hla_typing.hla_types_list,
                                        HLATypes.B.value),
                                    HLATypes.DR.value: get_filtered_antigens(
                                        pair.recipient.parameters.hla_typing.hla_types_list,
                                        HLATypes.DR.value),
                                    HLA_TYPE_OTHER: get_other_antigens(
                                        pair.recipient.parameters.hla_typing.hla_types_list)
                                },
                                recipient_antibodies={
                                    HLATypes.A.value: get_filtered_antibodies(pair.recipient.hla_antibodies,
                                                                              HLATypes.A.value),
                                    HLATypes.B.value: get_filtered_antibodies(pair.recipient.hla_antibodies,
                                                                              HLATypes.B.value),
                                    HLATypes.DR.value: get_filtered_antibodies(pair.recipient.hla_antibodies,
                                                                               HLATypes.DR.value),
                                    HLA_TYPE_OTHER: get_other_antibodies(pair.recipient.hla_antibodies)
                                },
                                antigens_score={
                                    HLATypes.A.value: calculate_antigen_score(pair.donor, pair.recipient,
                                                                              HLATypes.A.value),
                                    HLATypes.B.value: calculate_antigen_score(pair.donor, pair.recipient,
                                                                              HLATypes.B.value),
                                    HLATypes.DR.value: calculate_antigen_score(pair.donor, pair.recipient,
                                                                               HLATypes.DR.value)}
                            ) for pair in matching_round.donor_recipient_pairs])
                    for matching_round in matching.get_rounds()],
                countries=matching.get_country_codes_counts(),
                score=matching.score(),
                order_id=matching.order_id(),
                count_of_transplants=get_count_of_transplants(matching)
            )) for matching in matchings
        ]
        if get_user_role() == UserRole.VIEWER:
            matching_dtos = matching_dtos[:configuration.max_matchings_to_show_to_viewer]

        return jsonify(matching_dtos)
