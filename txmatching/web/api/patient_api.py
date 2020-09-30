# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from dacite import from_dict
from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.patients.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.patient_swagger import (
    DonorModel, DonorModelToUpdate, PatientsModel, RecipientModel,
    RecipientModelToUpdate)
from txmatching.data_transfer_objects.patients.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.services.patient_service import (get_txm_event,
                                                          update_donor,
                                                          update_recipient)
from txmatching.utils.logged_user import get_current_user
from txmatching.web.api.namespaces import patient_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@patient_api.route('/', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PatientsModel, description='')
    @require_user_login()
    def get(self) -> str:
        current_user = get_current_user()
        patients = get_txm_event(current_user.default_txm_event_id)
        return jsonify(patients.to_lists_for_fe())


@patient_api.route('/recipient', methods=['PUT'])
class AlterRecipient(Resource):

    @patient_api.doc(body=RecipientModelToUpdate, security='bearer')
    @patient_api.response(code=200, model=RecipientModel, description='')
    @require_user_login()
    def put(self):
        current_user = get_current_user()
        recipient_update_dto = from_dict(data_class=RecipientUpdateDTO, data=request.json)

        return jsonify(update_recipient(recipient_update_dto, current_user.default_txm_event_id))


@patient_api.route('/donor', methods=['PUT'])
class AlterDonor(Resource):
    @patient_api.doc(body=DonorModelToUpdate, security='bearer')
    @patient_api.response(code=200, model=DonorModel, description='')
    @require_user_login()
    def put(self):
        current_user = get_current_user()
        donor_update_dto = from_dict(data_class=DonorUpdateDTO, data=request.json)

        return jsonify(update_donor(donor_update_dto, current_user.default_txm_event_id))
