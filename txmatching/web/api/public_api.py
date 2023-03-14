import logging

from flask import request
from flask_restx import Resource

from tests.test_utilities.hla_preparation_utils import create_hla_typing, create_antibodies, create_antibody
from txmatching.auth.operation_guards.country_guard import \
    guard_user_has_access_to_country
from txmatching.auth.operation_guards.txm_event_guard import \
    guard_open_txm_event
from txmatching.auth.service.service_auth_check import allow_service_role
from txmatching.data_transfer_objects.external_patient_upload.do_crossmatch_dto import CrossmatchDTOIn, \
    CrossmatchDTOOut, HLAToAntibodyMatch
from txmatching.data_transfer_objects.external_patient_upload.swagger import (
    PatientUploadSuccessJson, UploadPatientsJson, CrossmatchJsonIn, CrossmatchJsonOut)
from txmatching.data_transfer_objects.patients.patient_parameters_dto import HLATypingRawDTO
from txmatching.data_transfer_objects.patients.patient_upload_dto_out import \
    PatientUploadPublicDTOOut
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.database.services.patient_upload_service import (
    get_patients_parsing_issues_from_upload_dto,
    replace_or_add_patients_from_one_country)
from txmatching.database.services.txm_event_service import (
    get_txm_event_db_id_by_name, save_original_data)
from txmatching.patients.hla_model import HLATypeRaw
from txmatching.utils.hla_system.hla_crossmatch import get_crossmatched_antibodies_per_group
from txmatching.utils.hla_system.hla_transformations.hla_transformations_store import \
    parse_hla_antibodies_raw_and_return_parsing_issue_list, parse_hla_typing_raw_and_return_parsing_issue_list
from txmatching.utils.logged_user import get_current_user_id
from txmatching.web.web_utils.namespaces import public_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

logger = logging.getLogger(__name__)


@public_api.route('/patient-upload', methods=['PUT'])
class TxmEventUploadPatients(Resource):

    @public_api.doc(security='bearer')
    @public_api.request_body(
        UploadPatientsJson,
        description='This endpoint allows the country editor to upload patient data for given '
                    'TXM event. TXM event name has to be provided by an ADMIN. You can either add patients to the '
                    'current dataset or remove all patients from respective country in case there were any. To '
                    'access this endpoint one has to have credentials to service account and obtain jwt token via the'
                    ' login endpoint.'
    )
    @public_api.response_ok(PatientUploadSuccessJson)
    @public_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @allow_service_role()
    def put(self):
        patient_upload_dto = request_body(PatientUploadDTOIn)
        country_code = patient_upload_dto.country

        current_user_id = get_current_user_id()
        # check if user is allowed to modify resources to the country
        guard_user_has_access_to_country(current_user_id, country_code)
        # check that txm event is opened
        txm_event_db_id = get_txm_event_db_id_by_name(patient_upload_dto.txm_event_name)
        guard_open_txm_event(txm_event_db_id)
        # save the original request to the database
        save_original_data(patient_upload_dto.txm_event_name, current_user_id, request.json)
        # perform update operation
        donors, recipients = replace_or_add_patients_from_one_country(patient_upload_dto)
        # Get parsing issues for uploaded patients
        parsing_issues = get_patients_parsing_issues_from_upload_dto(donors, recipients, txm_event_db_id)
        return response_ok(PatientUploadPublicDTOOut(
            recipients_uploaded=len(patient_upload_dto.recipients),
            donors_uploaded=len(patient_upload_dto.donors),
            parsing_issues=parsing_issues
        ))


@public_api.route('/do-crossmatch', methods=['POST'])
class TxmEventDoCrossmatch(Resource):
    @public_api.doc(security='bearer')
    @public_api.request_body(CrossmatchJsonIn)
    @public_api.response_ok(CrossmatchJsonOut)
    @public_api.response_errors(exceptions=set(), add_default_namespace_errors=True)
    @public_api.require_user_login()
    def post(self):
        crossmatch_dto = request_body(CrossmatchDTOIn)

        antibodies_list = [create_antibody(antibody.name, antibody.mfi, antibody.cutoff) for antibody in
                           crossmatch_dto.recipient_antibodies]

        crossmatched_antibodies_per_group = get_crossmatched_antibodies_per_group(
            donor_hla_typing=create_hla_typing(crossmatch_dto.donor_hla_typing),
            recipient_antibodies=create_antibodies(antibodies_list),
            use_high_resolution=True)

        antibodies_parsing_issues, _ = parse_hla_antibodies_raw_and_return_parsing_issue_list(
            antibodies_list)
        typing_parsing_issues, hla_per_group = parse_hla_typing_raw_and_return_parsing_issue_list(HLATypingRawDTO(
            hla_types_list=[HLATypeRaw(hla_type) for hla_type in crossmatch_dto.donor_hla_typing]
        ))

        antigen_to_antibody = [HLAToAntibodyMatch(hla_code=hla, antibody_matches=[]) for hla in
                               crossmatch_dto.donor_hla_typing]
        for match_per_group in crossmatched_antibodies_per_group:
            for match in match_per_group.antibody_matches:
                # get HLAToAntibodyMatch object with the same hla_code as the match
                [hla for hla in antigen_to_antibody if hla.hla_code == match.hla_antibody.raw_code][
                    0].antibody_matches.append(
                    match)

        return response_ok(CrossmatchDTOOut(
            hla_to_antibody=antigen_to_antibody,
            parsing_issues=antibodies_parsing_issues + typing_parsing_issues
        ))
