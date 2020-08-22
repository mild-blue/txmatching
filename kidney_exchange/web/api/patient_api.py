# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import dataclasses
import logging

from flask import jsonify
from flask_restx import Resource

from kidney_exchange.data_transfer_objects.patients.patient_swagger import PATIENT_MODEL
from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.web.api.namespaces import patient_api
from kidney_exchange.web.auth.login_check import login_required

logger = logging.getLogger(__name__)


@patient_api.route('/', methods=['GET'])
class Patient(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PATIENT_MODEL, description='')
    @login_required()
    def get(self) -> str:
        patients = list(get_all_patients())
        return jsonify([dataclasses.asdict(patient) for patient in patients])
