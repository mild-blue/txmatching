# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import dataclasses
import logging

from flask import jsonify
from flask_restx import Resource

from txmatching.data_transfer_objects.patients.patient_swagger import PATIENT_MODEL
from txmatching.database.services.patient_service import get_all_patients
from txmatching.web.api.namespaces import patient_api
from txmatching.web.auth.login_check import login_required

logger = logging.getLogger(__name__)


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@patient_api.route('/', methods=['GET'])
class Patient(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PATIENT_MODEL, description='')
    @login_required()
    def get(self) -> str:
        patients = list(get_all_patients())
        return jsonify([dataclasses.asdict(patient) for patient in patients])
