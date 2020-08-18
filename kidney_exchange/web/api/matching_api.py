import dataclasses
import json
import logging

import flask
from flask import request, Response, Blueprint
from flask_restx import Namespace

from kidney_exchange.data_transfer_objects.configuration.configuration_from_dto import \
    configuration_from_dto
from kidney_exchange.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, Transplant)
from kidney_exchange.database.services.config_service import \
    save_configuration_as_current
from kidney_exchange.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.solve_service.solve_from_db import solve_from_db

logger = logging.getLogger(__name__)

matching_api = Namespace('matching')
matching_blueprint = Blueprint('matching', __name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@matching_blueprint.route('/get-matchings', methods=['POST'])
def get_matchings() -> str:
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(request.json)
        save_configuration_as_current(configuration)
        solve_from_db()
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix()

        matching_dtos = [
            dataclasses.asdict(MatchingDTO(
                rounds=[
                    RoundDTO(
                        transplants=[
                            Transplant(
                                score_dict[(donor.db_id, recipient.db_id)],
                                compatible_blood_dict[(donor.db_id, recipient.db_id)],
                                donor.medical_id,
                                recipient.medical_id) for donor, recipient in round.donor_recipient_list])
                    for round in matching.get_rounds()],
                countries=matching.get_country_codes_counts(),
                score=matching.score()
            )) for matching in matchings
        ]

        json_data = json.dumps(matching_dtos)

        return Response(json_data, mimetype='application/json')


@matching_blueprint.route('/get-patients', methods=['GET'])
def get_patients() -> str:
    patients = list(get_all_patients())
    json_data = json.dumps([dataclasses.asdict(patient) for patient in patients])
    return Response(json_data, mimetype='application/json')
