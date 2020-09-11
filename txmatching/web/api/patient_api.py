# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from dacite import from_dict
from flask import jsonify, request
from flask_restx import Resource

from txmatching.data_transfer_objects.patients.patient_swagger import PATIENTS_MODEL, RECIPIENT_MODEL, DONOR_MODEL
from txmatching.database.services.patient_service import get_all_donors_recipients, save_recipient, save_donor
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.patients.patient import Recipient, Donor
from txmatching.web.api.namespaces import patient_api
from txmatching.web.auth.login_check import login_required

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@patient_api.route('/', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PATIENTS_MODEL, description='')
    @login_required()
    def get(self) -> str:
        patients = get_all_donors_recipients()
        return jsonify(patients.to_lists_for_fe())


@patient_api.route('/recipient', methods=['PUT'])
class AlterRecipient(Resource):

    @patient_api.doc(body={"db_id": int}, security='bearer')
    @patient_api.response(code=200, model=RECIPIENT_MODEL, description='')
    @login_required()
    def put(self):
        # TODO do not delete https://trello.com/c/zseK1Zcf
        ConfigModel.query.filter(ConfigModel.id > 0).delete()
        recipient = from_dict(data_class=Recipient, data=request.json)
        return jsonify({"db_id": save_recipient(recipient)})


@patient_api.route('/donor', methods=['PUT'])
class AlterDonor(Resource):
    @patient_api.doc(body={"db_id": int}, security='bearer')
    @patient_api.response(code=200, model=DONOR_MODEL, description='')
    @login_required()
    def put(self):
        # TODO do not delete https://trello.com/c/zseK1Zcf
        ConfigModel.query.filter(ConfigModel.id > 0).delete()
        donor = from_dict(data_class=Donor, data=request.json)
        return jsonify({"db_id": save_donor(donor)})
