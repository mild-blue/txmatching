# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask import jsonify
from flask_restx import Resource

from txmatching.data_transfer_objects.matchings.matching_swagger import MATCHING_MODEL
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix, get_matching_dtos
from txmatching.web.api.namespaces import dummy_matching_api

logger = logging.getLogger(__name__)

LOGIN_FLASH_CATEGORY: str = 'LOGIN'
MAX_MATCHINGS_TO_SHOW_TO_VIEWER: int = 50


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@dummy_matching_api.route('/', methods=['GET'])
class CalculateFromConfig(Resource):
    @dummy_matching_api.doc(security='bearer')
    @dummy_matching_api.response(
        code=200,
        model=MATCHING_MODEL,
        description='Dummy matching resource with sample data for presentation.'
    )
    def get(self) -> str:
        """
        Ges dummy matching for presentation and test purposes.
        :return:
        """
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix()
        matching_dtos = get_matching_dtos(matchings, score_dict, compatible_blood_dict)[
                        :MAX_MATCHINGS_TO_SHOW_TO_VIEWER]
        return jsonify(matching_dtos)
