# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging

from dacite import from_dict
from flask import jsonify, make_response, request
from flask_restx import Resource

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmDefaultEventDTOIn, TxmEventDTOIn)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import (
    TxmEventDTOOut, TxmEventsDTOOut)
from txmatching.data_transfer_objects.shared_swagger import FailJson
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmDefaultEventJsonIn, TxmEventJsonIn, TxmEventJsonOut, TxmEventsJson)
from txmatching.database.services.txm_event_service import (
    create_txm_event, delete_txm_event,
    get_allowed_txm_event_ids_for_current_user, get_txm_event_base,
    get_txm_event_id_for_current_user,
    update_default_txm_event_id_for_current_user)
from txmatching.web.web_utils.namespaces import txm_event_api

logger = logging.getLogger(__name__)


@txm_event_api.route('', methods=['POST', 'GET'])
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
        return make_response(jsonify(TxmEventDTOOut(id=created_event.db_id, name=created_event.name,
                                                    default_config_id=created_event.default_config_id)), 201)

    @txm_event_api.doc(
        security='bearer',
        description='Get list of allowed txm txmEvents for the logged user.'
    )
    @txm_event_api.response(code=200, model=TxmEventsJson, description='List of allowed txmEvents.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def get(self) -> str:
        txm_events = [
            get_txm_event_base(e) for e in
            get_allowed_txm_event_ids_for_current_user()
        ]
        txm_events_dto = [
            TxmEventDTOOut(id=e.db_id, name=e.name, default_config_id=e.default_config_id) for e in
            txm_events
        ]
        return jsonify(TxmEventsDTOOut(
            events=txm_events_dto
        ))


@txm_event_api.route('/default', methods=['PUT', 'GET'])
class TxmDefaultEventApi(Resource):

    @txm_event_api.doc(
        body=TxmDefaultEventJsonIn,
        security='bearer',
        description='Set default txm event for the logged user.'
    )
    @txm_event_api.response(code=200, model=TxmEventJsonOut, description='Returns the default event.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=409, model=FailJson, description='Non-unique patients provided.')
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def put(self):
        default_event_in = from_dict(data_class=TxmDefaultEventDTOIn, data=request.json)
        update_default_txm_event_id_for_current_user(default_event_in.id)
        event = get_txm_event_base(default_event_in.id)

        return make_response(jsonify(TxmEventDTOOut(id=event.db_id, name=event.name,
                                                    default_config_id=event.default_config_id)))

    @txm_event_api.doc(
        security='bearer',
        description='Get default event'
    )
    @txm_event_api.response(code=200, model=TxmEventJsonOut, description='Default event.')
    @txm_event_api.response(code=400, model=FailJson, description='Wrong data format.')
    @txm_event_api.response(code=401, model=FailJson, description='Authentication failed.')
    @txm_event_api.response(code=403, model=FailJson,
                            description='Access denied. You do not have rights to access this endpoint.'
                            )
    @txm_event_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def get(self) -> str:
        txm_event = get_txm_event_base(get_txm_event_id_for_current_user())
        return jsonify(TxmEventDTOOut(
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
