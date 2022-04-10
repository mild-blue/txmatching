# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.

import logging
from typing import Optional

from flask import request
from flask_restx import Resource

from txmatching.auth.auth_check import (require_role, require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.auth.operation_guards.country_guard import (
    get_user_default_country, guard_user_country_access_to_donor,
    guard_user_country_access_to_recipient, guard_user_has_access_to_country)
from txmatching.auth.operation_guards.txm_event_guard import \
    guard_open_txm_event
from txmatching.auth.user.user_auth_check import \
    require_user_edit_patients_access
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigIdPathParamDefinition
from txmatching.data_transfer_objects.external_patient_upload.swagger import \
    PatientUploadSuccessJson
from txmatching.data_transfer_objects.patients.out_dtos.conversions import (
    donor_to_donor_dto_out, recipient_to_recipient_dto_out, to_lists_for_fe)
from txmatching.data_transfer_objects.patients.out_dtos.donor_dto_out import \
    UpdatedDonorDTOOut
from txmatching.data_transfer_objects.patients.out_dtos.recipient_dto_out import \
    UpdatedRecipientDTOOut
from txmatching.data_transfer_objects.patients.patient_in_swagger import (
    DonorModelPairInJson, DonorToUpdateJson, PatientsJson,
    RecipientToUpdateJson, UpdatedDonorJsonOut, UpdatedRecipientJsonOut)
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadPublicDTOOut
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import \
    DonorRecipientPairDTO
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    PatientsRecomputeParsingSuccessJson
from txmatching.database.services.config_service import \
    get_configuration_parameters_from_db_id_or_default
from txmatching.database.services.patient_service import (
    delete_donor_recipient_pair, get_donor_recipient_pair,
    recompute_hla_and_antibodies_parsing_for_all_patients_in_txm_event,
    update_donor, update_recipient)
from txmatching.database.services.patient_upload_service import (
    add_donor_recipient_pair, get_patients_errors_from_pair_dto,
    replace_or_add_patients_from_excel)
from txmatching.database.services.txm_event_service import (
    get_txm_event_base, get_txm_event_complete)
from txmatching.database.services.upload_service import save_uploaded_file
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.hla_system.hla_transformations.parsing_error import \
    get_parsing_errors_for_patients
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.web_utils.namespaces import patient_api
from txmatching.web.web_utils.route_utils import (request_arg_flag,
                                                  request_body, response_ok, overriding_error)

logger = logging.getLogger(__name__)


@patient_api.route('/configs/<config_id>', methods=['GET'])
class AllPatients(Resource):

    @patient_api.doc(
        params={'config_id': ConfigIdPathParamDefinition},
        description='Get all patients for the given txm event.  '
                    'Example: /patients?include-antibodies-raw'
    )
    @patient_api.request_arg_flag(
        'include-antibodies-raw',
        'Specify to include raw antibodies as well. '
        'By default, raw antibodies are not included.'
    )
    @patient_api.require_user_login()
    @patient_api.response_ok(PatientsJson, description='List of donors and list of recipients.')
    @patient_api.response_errors()
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        include_antibodies_raw = request_arg_flag('include-antibodies-raw')
        logger.debug(f'include_antibodies_raw={include_antibodies_raw}')
        txm_event = get_txm_event_complete(txm_event_id, load_antibodies_raw=include_antibodies_raw)
        configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, config_id)
        lists_for_fe = to_lists_for_fe(txm_event, configuration_parameters)
        logger.debug('Sending patients to FE')
        return response_ok(lists_for_fe)


@patient_api.route('/pairs', methods=['POST'])
class DonorRecipientPairs(Resource):
    @patient_api.require_user_login()
    @patient_api.request_body(DonorModelPairInJson)
    @patient_api.response_ok(PatientUploadSuccessJson, 'Added new donor (possibly with recipient)')
    @patient_api.response_errors()
    @require_user_edit_patients_access()
    @require_valid_txm_event_id()
    def post(self, txm_event_id: int):
        donor_recipient_pair_dto_in = request_body(DonorRecipientPairDTO)

        guard_user_has_access_to_country(user_id=get_current_user_id(),
                                         country=donor_recipient_pair_dto_in.country_code)
        guard_open_txm_event(txm_event_id)

        donors, recipients = add_donor_recipient_pair(donor_recipient_pair_dto_in, txm_event_id)

        parsing_errors = get_patients_errors_from_pair_dto(donors, recipients, txm_event_id)

        return response_ok(PatientUploadPublicDTOOut(
            donors_uploaded=1,
            recipients_uploaded=1 if donor_recipient_pair_dto_in.recipient else 0,
            parsing_errors=parsing_errors
        ))


@patient_api.route('/pairs/<int:donor_db_id>', methods=['DELETE'])
class DonorRecipientPair(Resource):
    @patient_api.doc(
        params={
            'donor_db_id': {
                'description': 'Donor id that will be deleted including its recipient if there is any',
                'type': int,
                'required': True,
                'in': 'path'
            }
        },
        security='bearer',
        description='Delete existing donor recipient pair.'
    )
    @patient_api.response_ok(
        description='Returns status code representing result of donor recipient pair object deletion.'
    )
    @patient_api.response_errors()
    @require_user_edit_patients_access()
    @require_valid_txm_event_id()
    def delete(self, txm_event_id: int, donor_db_id: int):
        donor, maybe_recipient = get_donor_recipient_pair(donor_id=donor_db_id, txm_event_id=txm_event_id)

        guard_user_has_access_to_country(user_id=get_current_user_id(),
                                         country=donor.parameters.country_code)
        guard_open_txm_event(txm_event_id)

        if maybe_recipient is not None:
            guard_user_has_access_to_country(user_id=get_current_user_id(),
                                             country=maybe_recipient.parameters.country_code)

        delete_donor_recipient_pair(donor_id=donor_db_id, txm_event_id=txm_event_id)


@patient_api.route('/recipient', methods=['PUT'])
class AlterRecipient(Resource):
    @patient_api.require_user_login()
    @patient_api.request_body(RecipientToUpdateJson)
    @patient_api.response_ok(UpdatedRecipientJsonOut, description='Updated recipient.')
    @patient_api.response_errors()
    @patient_api.overriding_error()
    @require_user_edit_patients_access()
    @require_valid_txm_event_id()
    def put(self, txm_event_id: int):
        recipient_update_dto = request_body(RecipientUpdateDTO)
        guard_user_country_access_to_recipient(user_id=get_current_user_id(), recipient_id=recipient_update_dto.db_id)
        guard_open_txm_event(txm_event_id)
        updated_recipient, someone_is_overriding_patient = update_recipient(recipient_update_dto, txm_event_id)

        if not someone_is_overriding_patient:
            return response_ok(
                UpdatedRecipientDTOOut(
                    recipient=recipient_to_recipient_dto_out(updated_recipient),
                    parsing_errors=get_parsing_errors_for_patients(recipient_ids=[updated_recipient.db_id],
                                                                   txm_event_id=txm_event_id)
                )
            )
        else:
            return overriding_error()


@patient_api.route('/configs/<config_id>/donor', methods=['PUT'])
class AlterDonor(Resource):
    @patient_api.doc(params={'config_id': ConfigIdPathParamDefinition})
    @patient_api.require_user_login()
    @patient_api.request_body(DonorToUpdateJson)
    @patient_api.response_ok(UpdatedDonorJsonOut, description='Updated donor.')
    @patient_api.response_errors()
    @patient_api.overriding_error()
    @require_user_edit_patients_access()
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def put(self, txm_event_id: int, config_id: Optional[int]):
        donor_update_dto = request_body(DonorUpdateDTO)
        guard_user_country_access_to_donor(user_id=get_current_user_id(), donor_id=donor_update_dto.db_id)
        guard_open_txm_event(txm_event_id)
        txm_event = get_txm_event_complete(txm_event_id)
        all_recipients = txm_event.all_recipients
        configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event=txm_event,
                                                                                      configuration_db_id=config_id)
        scorer = scorer_from_configuration(configuration_parameters)
        updated_donor, someone_is_overriding_patient = update_donor(donor_update_dto, txm_event_id)

        if not someone_is_overriding_patient:
            return response_ok(
                UpdatedDonorDTOOut(
                    donor=donor_to_donor_dto_out(
                        updated_donor,
                        all_recipients,
                        configuration_parameters,
                        scorer
                    ),
                    parsing_errors=get_parsing_errors_for_patients(donor_ids=[updated_donor.db_id],
                                                                   txm_event_id=txm_event_id)
                )
            )
        else:
            return overriding_error()


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
    @patient_api.response_ok(PatientUploadSuccessJson, description='Success.')
    @patient_api.response_errors()
    @require_user_edit_patients_access()
    @require_valid_txm_event_id()
    def put(self, txm_event_id: int):
        guard_open_txm_event(txm_event_id)

        file = request.files['file']
        file_bytes = file.read()
        txm_event_name = get_txm_event_base(txm_event_id).name
        user_id = get_current_user_id()
        save_uploaded_file(file_bytes, file.filename, txm_event_id, user_id)

        if file.filename.endswith('multi_country.xlsx'):
            parsed_data = parse_excel_data(file_bytes, txm_event_name, None)
        elif file.filename.endswith('.xlsx'):
            parsed_data = parse_excel_data(file_bytes, txm_event_name, get_user_default_country(user_id))

        elif file.filename.endswith('.csv'):
            # TODO parse csv according to agreement with Austria https://github.com/mild-blue/txmatching/issues/287
            raise InvalidArgumentException('We cannot parse csv at the moment.')
        else:
            raise InvalidArgumentException('Unexpected file format.')

        for parsed_country_data in parsed_data:
            guard_user_has_access_to_country(user_id=user_id, country=parsed_country_data.country)

        replace_or_add_patients_from_excel(parsed_data)
        return response_ok(PatientUploadPublicDTOOut(
            recipients_uploaded=sum(len(parsed_data_country.recipients) for parsed_data_country in parsed_data),
            donors_uploaded=sum(len(parsed_data_country.donors) for parsed_data_country in parsed_data),
            parsing_errors=[]  # TODO: https://github.com/mild-blue/txmatching/issues/619
        ))


@patient_api.route('/recompute-parsing', methods=['POST'])
class RecomputeParsing(Resource):
    @patient_api.doc(
        description='Endpoint that lets an ADMIN recompute parsed antigens and antibodies for '
                    'all patients in the given txm event.'
    )
    @patient_api.response_ok(PatientsRecomputeParsingSuccessJson,
                             description='Returns the recomputation statistics.')
    @patient_api.response_errors()
    @require_role(UserRole.ADMIN)
    @require_valid_txm_event_id()
    def post(self, txm_event_id: int):
        result = recompute_hla_and_antibodies_parsing_for_all_patients_in_txm_event(txm_event_id)
        return response_ok(result)
