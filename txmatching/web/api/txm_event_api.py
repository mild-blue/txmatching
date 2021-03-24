# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask_restx import Resource

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmDefaultEventDTOIn, TxmEventDTOIn)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import (
    TxmEventDTOOut, TxmEventsDTOOut)
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmDefaultEventJsonIn, TxmEventJsonIn, TxmEventJsonOut, TxmEventsJson)
from txmatching.database.services.txm_event_service import (
    create_txm_event, delete_txm_event,
    get_allowed_txm_event_ids_for_current_user, get_txm_event_base,
    get_txm_event_id_for_current_user,
    update_default_txm_event_id_for_current_user)
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
            TxmEventDTOOut(id=created_event.db_id, name=created_event.name,
                           default_config_id=created_event.default_config_id),
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
            TxmEventDTOOut(id=e.db_id, name=e.name, default_config_id=e.default_config_id) for e in
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

        return response_ok(TxmEventDTOOut(id=event.db_id, name=event.name,
                                          default_config_id=event.default_config_id))

    @txm_event_api.doc(description='Get default event')
    @txm_event_api.require_user_login()
    @txm_event_api.response_ok(TxmEventJsonOut, description='Default event.')
    @txm_event_api.response_errors()
    def get(self) -> str:
        txm_event = get_txm_event_base(get_txm_event_id_for_current_user())
        return response_ok(TxmEventDTOOut(
            id=txm_event.db_id,
            name=txm_event.name,
            default_config_id=txm_event.default_config_id
        ))


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
    @txm_event_api.response_ok(description='Returns status code representing result of TXM event object deletion.')
    @txm_event_api.response_errors()
    @require_role(UserRole.ADMIN)
    def delete(self, name: str):
        delete_txm_event(name)
