# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging
from enum import Enum

from dacite import Config, from_dict
from flask import jsonify, make_response, request
from flask_restx import Resource

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole
from txmatching.auth.operation_guards.country_guard import \
    guard_user_has_access_to_country
from txmatching.auth.service.service_auth_check import allow_service_role
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadDTOOut
from txmatching.data_transfer_objects.patients.txm_event_dto_in import \
    TxmEventDTOIn
from txmatching.data_transfer_objects.patients.txm_event_dto_out import \
    TxmEventDTOOut
from txmatching.data_transfer_objects.patients.upload_dto.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    FailJson, PatientUploadSuccessJson, TxmEventJsonIn, TxmEventJsonOut,
    UploadPatientsJson)
from txmatching.database.services.patient_service import \
    update_txm_event_patients
from txmatching.database.services.txm_event_service import (create_txm_event,
                                                            delete_txm_event,
                                                            save_original_data)
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.api.namespaces import txm_event_api

logger = logging.getLogger(__name__)


@txm_event_api.route('', methods=['POST'])
class TxmEventApi(Resource):

    @txm_event_api.doc(
        body=TxmEventJsonIn,
        security='bearer',
        description='Endpoint that lets an ADMIN create a new TXM event. The ADMIN should specify TXM event name.'
    )
    @txm_event_api.response(code=201, model=TxmEventJsonOut, description='Returns the newly created TXM event object.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=409, model=FailJson, description='Non-unique patients provided.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_role(UserRole.ADMIN)
    def post(self):
        tmx_event = from_dict(data_class=TxmEventDTOIn, data=request.json)
        created_event = create_txm_event(tmx_event.name)
        return make_response(jsonify(TxmEventDTOOut(name=created_event.name)), 201)


# noinspection PyUnresolvedReferences
# because Pycharm clearly does not know how what that is
@txm_event_api.route('/<name>', methods=['DELETE'])
class TxmEventDeleteApi(Resource):

    @txm_event_api.doc(
        params={
            'name': {
                'description': 'Name of the TXM event to be deleted.',
                'type': str,
                'required': True,
                'in': 'path'
            }
        },
        security='bearer',
        description='Endpoint that lets an ADMIN delete existing TXM event. The ADMIN should know the TXM event name.'
    )
    @txm_event_api.response(
        code=200,
        model=None,
        description='Returns status code representing result of TXM event object deletion.'
    )
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_role(UserRole.ADMIN)
    def delete(self, name: str):
        delete_txm_event(name)


@txm_event_api.route('/patients', methods=['PUT'])
class TxmEventUploadPatients(Resource):

    @txm_event_api.doc(
        body=UploadPatientsJson,
        security='bearer',
        description='This endpoint allows the country editor to upload patient data for given \
                        TXM event. TXM event name has to be provided by an ADMIN. The endpoint removes all patients \
                        from respective country in case there were any.'
    )
    @txm_event_api.response(code=200, model=PatientUploadSuccessJson, description='Success.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @allow_service_role()
    def put(self):
        patient_upload_dto = from_dict(data_class=PatientUploadDTOIn, data=request.json, config=Config(cast=[Enum]))
        country_code = patient_upload_dto.country

        current_user_id = get_current_user_id()
        # check if user is allowed to modify resources to the country
        guard_user_has_access_to_country(current_user_id, country_code)
        # save the original request to the database
        save_original_data(patient_upload_dto.txm_event_name, current_user_id, request.json)
        # perform update operation
        update_txm_event_patients(patient_upload_dto, country_code)
        return jsonify(PatientUploadDTOOut(
            recipients_uploaded=len(patient_upload_dto.recipients),
            donors_uploaded=len(patient_upload_dto.donors)
        ))
