import dataclasses
import logging

from flask import Blueprint, jsonify
from flask_restx import Resource

from kidney_exchange.data_transfer_objects.patients.patient_swagger import PATIENT_MODEL
from kidney_exchange.database.services.patient_service import get_all_patients
from kidney_exchange.web.api.namespaces import patient_api, PATIENT_NAMESPACE

logger = logging.getLogger(__name__)

patient_blueprint = Blueprint(PATIENT_NAMESPACE, __name__)


@patient_api.route('/', methods=['GET'])
class Patient(Resource):

    @patient_api.response(code=200, model=PATIENT_MODEL, description="")
    def get(self) -> str:
        patients = list(get_all_patients())
        return jsonify([dataclasses.asdict(patient) for patient in patients])
