# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask import request
from flask_restx import Resource

from txmatching.auth.operation_guards.country_guard import \
    guard_user_has_access_to_country
from txmatching.auth.operation_guards.txm_event_guard import \
    guard_open_txm_event
from txmatching.auth.service.service_auth_check import allow_service_role
from txmatching.data_transfer_objects.external_patient_upload.swagger import (
    PatientUploadSuccessJson, UploadPatientsJson)
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadDTOOut
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.database.services.patient_upload_service import (
    get_patients_errors_from_upload_dto,
    replace_or_add_patients_from_one_country)
from txmatching.database.services.txm_event_service import (
    get_txm_event_db_id_by_name, save_original_data)
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.web_utils.namespaces import public_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

logger = logging.getLogger(__name__)


@public_api.route('/patient-upload', methods=['PUT'])
class TxmEventUploadPatients(Resource):

    @public_api.doc(security='bearer')
    @public_api.request_body(
        UploadPatientsJson,
        description='This endpoint allows the country editor to upload patient data for given '
                    'TXM event. TXM event name has to be provided by an ADMIN. You can either add patients to the '
                    'current dataset or remove all patients from respective country in case there were any. To '
                    'access this endpoint one has to have credentials to service account and obtain jwt token via the'
                    ' login endpoint.'
    )
    @public_api.response_ok(PatientUploadSuccessJson)
    @public_api.response_errors()
    @allow_service_role()
    def put(self):
        patient_upload_dto = request_body(PatientUploadDTOIn)
        country_code = patient_upload_dto.country

        current_user_id = get_current_user_id()
        # check if user is allowed to modify resources to the country
        guard_user_has_access_to_country(current_user_id, country_code)
        # check that txm event is opened
        txm_event_db_id = get_txm_event_db_id_by_name(patient_upload_dto.txm_event_name)
        guard_open_txm_event(txm_event_db_id)
        # save the original request to the database
        save_original_data(patient_upload_dto.txm_event_name, current_user_id, request.json)
        # perform update operation
        donors, recipients = replace_or_add_patients_from_one_country(patient_upload_dto)
        # Get parsing errors for uploaded patients
        parsing_errors = get_patients_errors_from_upload_dto(donors, recipients)
        return response_ok(PatientUploadDTOOut(
            recipients_uploaded=len(patient_upload_dto.recipients),
            donors_uploaded=len(patient_upload_dto.donors),
            parsing_errors=parsing_errors
        ))
