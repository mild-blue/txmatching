# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask_restx import Resource

from txmatching.auth.service.service_auth_check import allow_service_role
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmEventJsonIn, TxmEventJsonOut, UploadPatientsJson, FailJson, PatientUploadSuccessJson)
from txmatching.web.api.namespaces import txm_event_api

logger = logging.getLogger(__name__)


@txm_event_api.route('', methods=['PUT'])
class TxmEventApi(Resource):

    @txm_event_api.doc(body=TxmEventJsonIn, security='bearer',
                       description='Endpoint that lets an ADMIN create a new TXM event. \
                        The ADMIN should specify TXM event name.')
    @txm_event_api.response(code=200, model=TxmEventJsonOut,
                            description='Returns the newly created TXM event object.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication denied.')
    @txm_event_api.response(code=409, model=FailJson, description='Non-unique patients provided.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details.')
    @allow_service_role()
    def put(self):
        pass


@txm_event_api.route('/patients', methods=['PUT'])
class TxmEventUploadPatients(Resource):

    @txm_event_api.doc(body=UploadPatientsJson, security='bearer',
                       description='This endpoint allows the country editor to upload patient data for given \
                        TXM event. TXM event name has to be provided by an ADMIN. The endpoint removes all patients \
                        from respective country in case there were any.')
    @txm_event_api.response(code=200, description='Success.', model=PatientUploadSuccessJson)
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication denied.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected, see contents for details.')
    # TODO validate based on country of the user https://trello.com/c/8tzYR2Dj
    @allow_service_role()
    def put(self):
        # TODO add here the logic that will update patients https://trello.com/c/Yj70es9D
        pass
