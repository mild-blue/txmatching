# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask_restx import Resource
from flask import request

from txmatching.auth.auth_check import require_role, require_valid_txm_event_id
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.external_patient_upload.swagger import \
    UploadPatientsJson, CopyPatientsJson
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmDefaultEventDTOIn, TxmEventDTOIn, TxmEventExportDTOIn,
    TxmEventUpdateDTOIn, TxmEventCopyDTOIn)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import \
    TxmEventsDTOOut
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmDefaultEventJsonIn, TxmEventExportJsonIn, TxmEventJsonIn,
    TxmEventJsonOut, TxmEventsJson, TxmEventUpdateJsonIn, TxmEventCopyJsonIn,
    )
from txmatching.database.services.txm_event_service import (
    convert_txm_event_base_to_dto, create_txm_event, delete_txm_event,
    get_allowed_txm_event_ids_for_current_user, get_txm_event_base,
    get_txm_event_id_for_current_user, set_txm_event_state,
    update_default_txm_event_id_for_current_user)
from txmatching.utils.export.export_txm_event import \
    get_patients_upload_json_from_txm_event_for_country
from txmatching.utils.copy.copy_patients_from_event_to_event import \
    get_patients_from_event, load_patients_to_event

from txmatching.web.web_utils.namespaces import txm_event_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

logger = logging.getLogger(__name__)


@txm_event_api.route('', methods=['POST', 'GET'])
class TxmEventApi(Resource):

    @txm_event_api.require_user_login()
    @txm_event_api.request_body(
        TxmEventJsonIn,
        description='Endpoint that lets an ADMIN create a new TXM event. The ADMIN should specify TXM event name.'
    )
    @txm_event_api.response_ok(model=TxmEventJsonOut, code=201,
                               description='Returns the newly created TXM event object.')
    @txm_event_api.response_errors()
    @txm_event_api.response_error_non_unique_patients_provided()
    @require_role(UserRole.ADMIN)
    def post(self):
        tmx_event = request_body(TxmEventDTOIn)
        created_event = create_txm_event(tmx_event.name)
        return response_ok(
            convert_txm_event_base_to_dto(created_event),
            code=201)

    @txm_event_api.doc(
        description='Get list of allowed txm txmEvents for the logged user.'
    )
    @txm_event_api.require_user_login()
    @txm_event_api.response_ok(TxmEventsJson, description='List of allowed txmEvents.')
    @txm_event_api.response_errors()
    def get(self) -> str:
        txm_events = [
            get_txm_event_base(e) for e in
            get_allowed_txm_event_ids_for_current_user()
        ]
        txm_events_dto = [
            convert_txm_event_base_to_dto(e) for e in
            txm_events
        ]
        return response_ok(TxmEventsDTOOut(
            events=txm_events_dto
        ))


@txm_event_api.route('/default', methods=['PUT', 'GET'])
class TxmDefaultEventApi(Resource):
    @txm_event_api.require_user_login()
    @txm_event_api.request_body(TxmDefaultEventJsonIn, 'Set default txm event for the logged user.')
    @txm_event_api.response_ok(TxmEventJsonOut, description='Returns the default event.')
    @txm_event_api.response_errors()
    @txm_event_api.response_error_non_unique_patients_provided()
    def put(self):
        default_event_in = request_body(TxmDefaultEventDTOIn)
        update_default_txm_event_id_for_current_user(default_event_in.id)
        event = get_txm_event_base(default_event_in.id)

        return response_ok(convert_txm_event_base_to_dto(event))

    @txm_event_api.doc(description='Get default event')
    @txm_event_api.require_user_login()
    @txm_event_api.response_ok(TxmEventJsonOut, description='Default event.')
    @txm_event_api.response_errors()
    def get(self) -> str:
        txm_event = get_txm_event_base(get_txm_event_id_for_current_user())
        return response_ok(convert_txm_event_base_to_dto(txm_event))

# noinspection PyUnresolvedReferences
@txm_event_api.route('/<int:txm_event_id>', methods=['PUT'])
class TxmEventUpdateApi(Resource):
    @txm_event_api.require_user_login()
    @txm_event_api.request_body(TxmEventUpdateJsonIn, 'TXM event parameters that should be updated.')
    @txm_event_api.response_ok(TxmEventJsonOut, description='Returns the updated TXM event.')
    @txm_event_api.response_errors()
    @require_role(UserRole.ADMIN)
    @require_valid_txm_event_id()
    def put(self, txm_event_id: int):
        update = request_body(TxmEventUpdateDTOIn)

        if update.state is not None:
            set_txm_event_state(txm_event_id, update.state)

        event = get_txm_event_base(txm_event_id)

        return response_ok(convert_txm_event_base_to_dto(event))


# noinspection PyUnresolvedReferences
# because Pycharm clearly does not know how what that is
@txm_event_api.route('/<int:txm_event_id>', methods=['DELETE'])
class TxmEventDeleteApi(Resource):

    @txm_event_api.doc(
        params={
            'txm_event_id': {
                'description': 'Id of the TXM event to be deleted.',
                'type': int,
                'required': True,
                'in': 'path'
            }
        },
        security='bearer',
        description='Endpoint that lets an ADMIN delete existing TXM event.'
    )
    @txm_event_api.response_ok(description='Returns status code representing result of TXM event object deletion.')
    @txm_event_api.response_errors()
    @require_role(UserRole.ADMIN)
    def delete(self, txm_event_id: int):
        delete_txm_event(txm_event_id)


# noinspection PyUnresolvedReferences
@txm_event_api.route('/<int:txm_event_id>/export', methods=['POST'])
class TxmExportEventApi(Resource):
    @txm_event_api.require_user_login()
    @require_role(UserRole.ADMIN)
    @txm_event_api.response_ok(UploadPatientsJson, description='Exported patients DTO, Ready to be uploaded to'
                                                               'some other event')  # ask patients from the server
    @txm_event_api.response_errors()
    @txm_event_api.request_body( 
        TxmEventExportJsonIn,
        description='Export patients from provided country and TXM event. Make the file ready to be'
                    'uploaded again with already new txm event name ready.'
    ) # where to export
    def post(self, txm_event_id: int) -> str:
        export_dto = request_body(TxmEventExportDTOIn) 
        txm_event_json = get_patients_upload_json_from_txm_event_for_country(
            txm_event_id=txm_event_id,
            country_code=export_dto.country,
            txm_event_name=export_dto.new_txm_event_name
        )
        return response_ok(txm_event_json)

#  ----------------------------------------------------------------------------------------------------------------------

'''
in all our other endpoint we use json objects to send data to the api, not the url path itself. 
'''

@txm_event_api.route('/copy', methods=['PUT'])
class TxmCopyPatientsBetweenEventsApi(Resource):
    @txm_event_api.require_user_login()
    @require_role(UserRole.ADMIN)
    @txm_event_api.doc(
        params={
            'txm_event_id_from': {
                'description': 'Id of the TXM event to be copied from.',
                'type': int,
                'required': True,
            },
            'txm_event_id_to': {
                'description': 'Id of the TXM event to be copied to.',
                'type': int,
                'required': True,
            },
            'donor_ids': {
                'description': 'Ids of the donors to be copied.',
                'type': list,
                'required': True,
            }
        },
        security='bearer',
        description='Endpoint that lets an ADMIN copy patients from one event to another.'
    )
    @txm_event_api.response_ok(
        CopyPatientsJson, 
        description="Patients were successfully copied. List of new patients ids: ")
    @txm_event_api.response_errors()
    @txm_event_api.request_body(
        TxmEventCopyJsonIn,
        description='Copy list of patients from one event to the other'
    )
    def put(self) -> str:
        copy_dto = request_body(TxmEventCopyDTOIn)
        donor_ids = copy_dto.donor_ids
        donor_ids = [int(donor_id) for donor_id in donor_ids] 

        patients_dto = get_patients_from_event(copy_dto.txm_event_id_from, donor_ids)
        new_patients_ids = load_patients_to_event(copy_dto.txm_event_id_to, patients_dto)

        return response_ok(new_patients_ids)                                                                                                    



    

