import dataclasses
import json
import logging

from flask import Response, Blueprint
from flask_restx import Resource

from kidney_exchange.data_transfer_objects.patients.patient_swagger import patient_model
from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.web.api.namespaces import patient_api

logger = logging.getLogger(__name__)

patient_blueprint = Blueprint('patients', __name__)


@patient_api.route('/', methods=['GET'])
class Patient(Resource):

    @patient_api.response(code=200, model=patient_model, description="")
    def get(self) -> str:
        patients = list(get_all_patients())
        json_data = json.dumps([dataclasses.asdict(patient) for patient in patients])
        return Response(json_data, mimetype='application/json')
