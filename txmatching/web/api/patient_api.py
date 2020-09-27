# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from dacite import from_dict
from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.login_check import login_required
from txmatching.data_transfer_objects.patients.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.patient_swagger import (
    DONOR_MODEL, DONOR_MODEL_TO_UPDATE, PATIENTS_MODEL, RECIPIENT_MODEL,
    RECIPIENT_MODEL_TO_UPDATE)
from txmatching.data_transfer_objects.patients.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.services.patient_service import (get_txm_event,
                                                          update_donor,
                                                          update_recipient)
from txmatching.web.api.namespaces import patient_api

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@patient_api.route('/', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PATIENTS_MODEL, description='')
    @login_required()
    def get(self) -> str:
        patients = get_txm_event()
        return jsonify(patients.to_lists_for_fe())


@patient_api.route('/recipient', methods=['PUT'])
class AlterRecipient(Resource):

    @patient_api.doc(body=RECIPIENT_MODEL_TO_UPDATE, security='bearer')
    @patient_api.response(code=200, model=RECIPIENT_MODEL, description='')
    @login_required()
    def put(self):
        recipient_update_dto = from_dict(data_class=RecipientUpdateDTO, data=request.json)

        return jsonify(update_recipient(recipient_update_dto))


@patient_api.route('/donor', methods=['PUT'])
class AlterDonor(Resource):
    @patient_api.doc(body=DONOR_MODEL_TO_UPDATE, security='bearer')
    @patient_api.response(code=200, model=DONOR_MODEL, description='')
    @login_required()
    def put(self):
        donor_update_dto = from_dict(data_class=DonorUpdateDTO, data=request.json)

        return jsonify(update_donor(donor_update_dto))
