import logging

from flask_restx import Resource

from txmatching.auth.auth_check import require_role, require_valid_txm_event_id
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import NonUniquePatient
from txmatching.data_transfer_objects.external_patient_upload.swagger import (
    CopyPatientsJsonOut, UploadPatientsJson)
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmDefaultEventDTOIn, TxmEventCopyPatientsDTOIn, TxmEventDTOIn,
    TxmEventExportDTOIn, TxmEventUpdateDTOIn)
from txmatching.data_transfer_objects.patients.txm_event_dto_out import (
    TxmEventCopyPatientsDTOOut, TxmEventsDTOOut)
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    TxmDefaultEventJsonIn, TxmEventCopyPatientsJsonIn, TxmEventExportJsonIn,
    TxmEventJsonIn, TxmEventJsonOut, TxmEventsJson, TxmEventUpdateJsonIn)
from txmatching.database.services.txm_event_service import (
    convert_txm_event_base_to_dto, create_txm_event, delete_txm_event,
    get_allowed_txm_event_ids_for_current_user, get_txm_event_base,
    get_txm_event_id_for_current_user, set_txm_event_state,
    update_default_txm_event_id_for_current_user)
from txmatching.utils.copy.copy_patients_from_event_to_event import \
    copy_patients_between_events
from txmatching.utils.export.export_txm_event import \
    get_patients_upload_json_from_txm_event_for_country
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
    @txm_event_api.response_errors(exceptions={NonUniquePatient}, add_default_namespace_errors=True)
    @require_role(UserRole.ADMIN)
    def post(self):
        txm_event = request_body(TxmEventDTOIn)
        created_event = create_txm_event(txm_event.name, txm_event.strictness_type)
        return response_ok(
            convert_txm_event_base_to_dto(created_event),
            code=201)

    @txm_event_api.doc(
        description='Get list of allowed txm txmEvents for the logged user.'
    )
    @txm_event_api.require_user_login()
    @txm_event_api.response_ok(TxmEventsJson, description='List of allowed txmEvents.')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
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
    @txm_event_api.response_errors(exceptions={NonUniquePatient}, add_default_namespace_errors=True)
    def put(self):
        default_event_in = request_body(TxmDefaultEventDTOIn)
        update_default_txm_event_id_for_current_user(default_event_in.id)
        event = get_txm_event_base(default_event_in.id)

        return response_ok(convert_txm_event_base_to_dto(event))

    @txm_event_api.doc(description='Get default event')
    @txm_event_api.require_user_login()
    @txm_event_api.response_ok(TxmEventJsonOut, description='Default event.')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    def get(self) -> str:
        txm_event = get_txm_event_base(get_txm_event_id_for_current_user())
        return response_ok(convert_txm_event_base_to_dto(txm_event))


# noinspection PyUnresolvedReferences


@txm_event_api.route('/<int:txm_event_id>', methods=['PUT'])
class TxmEventUpdateApi(Resource):
    @txm_event_api.require_user_login()
    @txm_event_api.request_body(TxmEventUpdateJsonIn, 'TXM event parameters that should be updated.')
    @txm_event_api.response_ok(TxmEventJsonOut, description='Returns the updated TXM event.')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
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
                'in': 'path',
                'default': 2
            }
        },
        security='bearer',
        description='Endpoint that lets an ADMIN delete existing TXM event.'
    )
    @txm_event_api.response_ok(description='Returns status code representing result of TXM event object deletion.')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @require_role(UserRole.ADMIN)
    def delete(self, txm_event_id: int):
        delete_txm_event(txm_event_id)


# noinspection PyUnresolvedReferences
@txm_event_api.route('/<int:txm_event_id>/export', methods=['POST'])
class TxmExportEventApi(Resource):
    @txm_event_api.require_user_login()
    @require_role(UserRole.ADMIN)
    @txm_event_api.response_ok(UploadPatientsJson, description='Exported patients DTO, Ready to be uploaded to '
                                                               'some other event')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @txm_event_api.request_body(
        TxmEventExportJsonIn,
        description='Export patients from provided country and TXM event. Make the file ready to be '
                    'uploaded again with already new txm event name ready.'
    )  # where to export
    def post(self, txm_event_id: int) -> str:
        export_dto = request_body(TxmEventExportDTOIn)
        txm_event_json = get_patients_upload_json_from_txm_event_for_country(
            txm_event_id=txm_event_id,
            country_code=export_dto.country,
            txm_event_name=export_dto.new_txm_event_name,
            strictness_type=export_dto.strictness_type
        )
        return response_ok(txm_event_json)


@txm_event_api.route('/copy', methods=['PUT'])
class TxmCopyPatientsBetweenEventsApi(Resource):
    @txm_event_api.require_user_login()
    @require_role(UserRole.ADMIN)
    @txm_event_api.response_ok(
        CopyPatientsJsonOut,
        description='Patients were successfully copied. List of new patients ids: ')
    @txm_event_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @txm_event_api.request_body(
        TxmEventCopyPatientsJsonIn,
        description='Copy list of patients from one event to the other'
    )
    def put(self) -> str:
        copy_dto = request_body(TxmEventCopyPatientsDTOIn)

        new_donor_ids = copy_patients_between_events(
            txm_event_id_from=copy_dto.txm_event_id_from,
            txm_event_id_to=copy_dto.txm_event_id_to,
            donor_ids=copy_dto.donor_ids)

        return response_ok(TxmEventCopyPatientsDTOOut(
            new_donor_ids=new_donor_ids
        ))
