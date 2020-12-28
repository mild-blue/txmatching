# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import logging

from dacite import from_dict
from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.operation_guards.country_guard import (
    guard_user_country_access_to_donor, guard_user_country_access_to_recipient)
from txmatching.auth.user.user_auth_check import (require_user_edit_access,
                                                  require_user_login)
from txmatching.data_transfer_objects.patients.patient_swagger import (
    DonorModel, DonorModelToUpdate, PatientsModel, RecipientModel,
    RecipientModelToUpdate)
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services.patient_service import (get_txm_event,
                                                          update_donor,
                                                          update_recipient, to_lists_for_fe, donor_to_donor_dto)
from txmatching.database.services.txm_event_service import \
    get_txm_event_id_for_current_user
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.api.namespaces import patient_api

logger = logging.getLogger(__name__)


@patient_api.route('', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PatientsModel, description='List of donors and list of recipients.')
    @patient_api.response(code=400, model=FailJson, description='Wrong data format.')
    @patient_api.response(code=401, model=FailJson, description='Authentication failed.')
    @patient_api.response(code=403, model=FailJson,
                          description='Access denied. You do not have rights to access this endpoint.'
                          )
    @patient_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    def get(self) -> str:
        txm_event = get_txm_event(get_txm_event_id_for_current_user())
        return jsonify(to_lists_for_fe(txm_event))


@patient_api.route('/recipient', methods=['PUT'])
class AlterRecipient(Resource):

    @patient_api.doc(body=RecipientModelToUpdate, security='bearer')
    @patient_api.response(code=200, model=RecipientModel, description='Updates single recipient.')
    @patient_api.response(code=400, model=FailJson, description='Wrong data format.')
    @patient_api.response(code=401, model=FailJson, description='Authentication failed.')
    @patient_api.response(code=403, model=FailJson,
                          description='Access denied. You do not have rights to access this endpoint.'
                          )
    @patient_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_edit_access()
    def put(self):
        recipient_update_dto = from_dict(data_class=RecipientUpdateDTO, data=request.json)
        guard_user_country_access_to_recipient(user_id=get_current_user_id(), recipient_id=recipient_update_dto.db_id)
        return jsonify(update_recipient(recipient_update_dto, get_txm_event_id_for_current_user()))


@patient_api.route('/donor', methods=['PUT'])
class AlterDonor(Resource):
    @patient_api.doc(body=DonorModelToUpdate, security='bearer')
    @patient_api.response(code=200, model=DonorModel, description='Updates single donor.')
    @patient_api.response(code=400, model=FailJson, description='Wrong data format.')
    @patient_api.response(code=401, model=FailJson, description='Authentication failed.')
    @patient_api.response(code=403, model=FailJson,
                          description='Access denied. You do not have rights to access this endpoint.'
                          )
    @patient_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_edit_access()
    def put(self):
        donor_update_dto = from_dict(data_class=DonorUpdateDTO, data=request.json)
        guard_user_country_access_to_donor(user_id=get_current_user_id(), donor_id=donor_update_dto.db_id)
        txm_event_db_id = get_txm_event_id_for_current_user()
        all_recipients = get_txm_event(txm_event_db_id).all_recipients
        return jsonify(donor_to_donor_dto(
            update_donor(donor_update_dto, get_txm_event_id_for_current_user()),
            all_recipients,
            txm_event_db_id)
        )
