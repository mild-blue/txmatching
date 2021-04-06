# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from flask_restx import Resource

from txmatching.auth.auth_check import require_role, require_valid_txm_event_id
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmDefaultEventDTOIn, TxmEventDTOIn, TxmEventUpdateDTOIn)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import \
    TxmEventsDTOOut
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmDefaultEventJsonIn, TxmEventJsonIn, TxmEventJsonOut, TxmEventsJson,
    TxmEventUpdateJsonIn)
from txmatching.database.services.txm_event_service import (
    convert_txm_event_base_to_dto, create_txm_event, delete_txm_event,
    get_allowed_txm_event_ids_for_current_user, get_txm_event_base,
    get_txm_event_id_for_current_user, set_txm_event_state,
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


@txm_event_api.route('/<int:txm_event_id>', methods=['PUT'])
class TxmEventUpdateApi(Resource):

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
