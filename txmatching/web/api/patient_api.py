# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import logging

from dacite import from_dict
from flask import jsonify, request
from flask_restx import Resource

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.auth.operation_guards.country_guard import (
    get_user_default_country, guard_user_country_access_to_donor,
    guard_user_country_access_to_recipient, guard_user_has_access_to_country)
from txmatching.auth.user.user_auth_check import (require_user_edit_access,
                                                  require_user_login)
from txmatching.data_transfer_objects.patients.patient_swagger import (
    DonorJson, DonorModelToUpdateJson, PatientsJson, RecipientJson,
    RecipientModelToUpdateJson)
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadDTOOut
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import (
    FailJson, PatientUploadSuccessJson)
from txmatching.database.services.patient_service import (
    donor_to_donor_dto, get_txm_event, save_patients_from_excel_to_txm_event,
    to_lists_for_fe, update_donor, update_recipient)
from txmatching.database.services.txm_event_service import \
    get_txm_event_id_for_current_user
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.api.namespaces import patient_api

logger = logging.getLogger(__name__)


@patient_api.route('', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(security='bearer')
    @patient_api.response(code=200, model=PatientsJson, description='List of donors and list of recipients.')
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

    @patient_api.doc(body=RecipientModelToUpdateJson, security='bearer')
    @patient_api.response(code=200, model=RecipientJson, description='Updates single recipient.')
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
    @patient_api.doc(body=DonorModelToUpdateJson, security='bearer')
    @patient_api.response(code=200, model=DonorJson, description='Updates single donor.')
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


@patient_api.route('/add-patients-file', methods=['PUT'])
class AddPatientsFile(Resource):

    @patient_api.doc(security='bearer',
                     params={'file': {
                         'name': 'file',
                         'in': 'formData',
                         'description': 'Excel file to upload data.',
                         'required': True,
                         'type': 'file'
                     }
                     }
                     )
    @patient_api.response(code=200, model=PatientUploadSuccessJson, description='Success.')
    @patient_api.response(code=400, model=FailJson, description='Wrong data format.')
    @patient_api.response(code=401, model=FailJson, description='Authentication failed.')
    @patient_api.response(code=403, model=FailJson,
                          description='Access denied. You do not have rights to access this endpoint.'
                          )
    @patient_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_edit_access()
    def put(self):
        file = request.files['file']
        txm_event_db_id = get_txm_event_id_for_current_user()
        txm_event_name = get_txm_event(txm_event_db_id).name
        user_id = get_current_user_id()

        if file.filename.endswith('multi_country.xlsx'):
            parsed_data = parse_excel_data(file, txm_event_name, None)
        elif file.filename.endswith('.xlsx'):
            parsed_data = parse_excel_data(file, txm_event_name, get_user_default_country(user_id))

        elif file.filename.endswith('.csv'):
            # TODO parse csv according to agreement with Austria https://github.com/mild-blue/txmatching/issues/287
            raise InvalidArgumentException('We cannot parse csv at the moment.')
        else:
            raise InvalidArgumentException('Unexpected file format.')

        for parsed_country_data in parsed_data:
            guard_user_has_access_to_country(user_id=user_id, country=parsed_country_data.country)
        # TODO save uploaded file to database for further investigation
        #  https://github.com/mild-blue/txmatching/issues/288
        save_patients_from_excel_to_txm_event(parsed_data)
        return jsonify(PatientUploadDTOOut(
            recipients_uploaded=sum(len(parsed_data_country.recipients) for parsed_data_country in parsed_data),
            donors_uploaded=sum(len(parsed_data_country.donors) for parsed_data_country in parsed_data))
        )
