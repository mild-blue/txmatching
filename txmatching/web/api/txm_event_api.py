# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging
from enum import Enum

from dacite import Config, from_dict
from flask import jsonify, make_response, request
from flask_restx import Resource

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole
from txmatching.auth.service.service_auth_check import allow_service_role
from txmatching.data_transfer_objects.patients.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadDTOOut
from txmatching.data_transfer_objects.patients.txm_event_dto_in import \
    TxmEventDTOIn
from txmatching.data_transfer_objects.patients.txm_event_dto_out import \
    TxmEventDTOOut
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    FailJson, PatientUploadSuccessJson, TxmEventJsonIn, TxmEventJsonOut,
    UploadPatientsJson)
from txmatching.database.services.patient_service import \
    update_txm_event_patients
from txmatching.database.services.txm_event_service import (create_txm_event,
                                                            delete_txm_event)
from txmatching.web.api.namespaces import txm_event_api

logger = logging.getLogger(__name__)


@txm_event_api.route('', methods=['POST'])
class TxmEventApi(Resource):

    @txm_event_api.doc(
        body=TxmEventJsonIn,
        security='bearer',
        description='Endpoint that lets an ADMIN create a new TXM event. \
                        The ADMIN should specify TXM event name.'
    )
    @txm_event_api.response(
        code=201,
        model=TxmEventJsonOut,
        description='Returns the newly created TXM event object.'
    )
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication denied.')
    @txm_event_api.response(code=409, model=FailJson, description='Non-unique patients provided.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details.')
    @require_role(UserRole.ADMIN)
    def post(self):
        tmx_event = from_dict(data_class=TxmEventDTOIn, data=request.json)
        created_event = create_txm_event(tmx_event.name)
        return make_response(jsonify(TxmEventDTOOut(name=created_event.name)), 201)


@txm_event_api.route('/<name>', methods=['DELETE'])
class TxmEventDeleteApi(Resource):

    @txm_event_api.doc(
        params={
            'name': {
                'description': 'Name of the TXM event to be deleted.',
                'in': 'query',
                'type': 'string',
                'required': 'true'
            }
        },
        security='bearer',
        description='Endpoint that lets an ADMIN delete existing TXM event. \
                        The ADMIN should specify TXM event name.'
    )
    @txm_event_api.response(
        code=200,
        model=None,
        description='Returns status code representing result of TXM event object deletion.'
    )
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication denied.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details.')
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
    @txm_event_api.response(code=401, model=FailJson, description='Authentication denied.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details.')
    # TODO validate based on country of the user https://trello.com/c/8tzYR2Dj
    @allow_service_role()
    def put(self):
        patient_upload_dto = from_dict(data_class=PatientUploadDTOIn, data=request.json, config=Config(cast=[Enum]))
        # TODO validate based on country of the user https://trello.com/c/8tzYR2Dj
        # current_user = get_current_user()
        country_code = patient_upload_dto.country  # TODO get from the user https://trello.com/c/8tzYR2Dj
        update_txm_event_patients(patient_upload_dto, country_code)
        return jsonify(PatientUploadDTOOut(
            recipients_uploaded=len(patient_upload_dto.recipients),
            donors_uploaded=len(patient_upload_dto.donors)
        ))
