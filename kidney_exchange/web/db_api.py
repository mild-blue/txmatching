import logging

from flask import Blueprint, request, redirect

from kidney_exchange.database.services.save_patients import save_patients
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data

logger = logging.getLogger(__name__)

db_api = Blueprint('db', __name__)


@db_api.route('/load_patients_to_db', methods=['POST'])
def load_patients_to_db():
    try:
        patient_data = request.files['patient_data']
        parsed_data = parse_excel_data(patient_data)
        save_patients(parsed_data)
        logger.info("Patients were saved successfully")
    except Exception as e:
        logger.error(f"Something went wrong when uploading: {e}")
    return redirect('/load_patients')
