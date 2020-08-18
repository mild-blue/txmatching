import logging
from typing import List

import flask
from flask import Blueprint, request
from flask_login import current_user

from kidney_exchange.data_transfer_objects.configuration.configuration_from_dto import \
    configuration_from_dto
from kidney_exchange.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, Transplant)
from kidney_exchange.database.services.config_service import \
    save_configuration_as_current
from kidney_exchange.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.patients.patient import Patient
from kidney_exchange.solve_service.solve_from_db import solve_from_db
from kidney_exchange.web.service_api import check_admin_or_editor

logger = logging.getLogger(__name__)

matching_api = Blueprint('matching', __name__)

LOGIN_FLASH_CATEGORY = 'LOGIN'


@matching_api.route('/get-matchings', methods=['POST'])
def get_matchings() -> List[MatchingDTO]:
    check_admin_or_editor(current_user.role)
    if flask.request.method == 'POST':
        configuration = configuration_from_dto(request.json)
        save_configuration_as_current(configuration)
        solve_from_db()
        matchings, score_dict, compatible_blood_dict = get_latest_matchings_and_score_matrix()

        matching_dtos = [
            MatchingDTO(
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
            ) for matching in matchings
        ]

        return matching_dtos


@matching_api.route('/get-matchings', methods=['GET'])
def get_patients() -> List[Patient]:
    check_admin_or_editor(current_user.role)
    return list(get_all_patients())
