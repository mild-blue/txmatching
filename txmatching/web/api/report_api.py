import logging
from typing import Optional

from flask import send_file, send_from_directory
from flask_restx import Resource

from txmatching.auth.auth_check import (require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.exceptions import NotFoundException
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigIdPathParamDefinition
from txmatching.data_transfer_objects.patients.out_dtos.conversions import \
    to_lists_for_fe
from txmatching.database.services.config_service import (
    get_configuration_from_db_id_or_default,
    get_configuration_parameters_from_db_id_or_default,
    save_config_parameters_to_db)
from txmatching.database.services.pairing_result_service import \
    get_pairing_result_comparable_to_config_or_solve
from txmatching.database.services.report_service import (
    ReportConfiguration, export_patients_to_xlsx_file, generate_pdf_report)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.logged_user import get_current_user_id
from txmatching.utils.time import get_formatted_now
from txmatching.web.web_utils.namespaces import report_api
from txmatching.web.web_utils.route_utils import (request_arg_flag,
                                                  request_arg_int)

logger = logging.getLogger(__name__)

MATCHINGS_BELOW_CHOSEN_PARAM = 'matchingsBelowChosen'
INCLUDE_PATIENTS_SECTION_PARAM = 'includePatientsSection'
MIN_MATCHINGS_BELOW_CHOSEN = 0
MAX_MATCHINGS_BELOW_CHOSEN = 20


# Query params:
#   - matchingRangeLimit
@report_api.route('/configs/<config_id>/matchings/<int:matching_id>/pdf', methods=['GET'])
class MatchingReport(Resource):

    @report_api.doc(
        params={
            'matching_id': {
                'description': 'Id of matching that was chosen',
                'type': int,
                'in': 'path',
                'required': True
            },
            'config_id': ConfigIdPathParamDefinition
        }
    )
    @report_api.request_arg_int(MATCHINGS_BELOW_CHOSEN_PARAM,
                                'Number of matchings with lower score than chosen to include in report.')
    @report_api.request_arg_flag(INCLUDE_PATIENTS_SECTION_PARAM,
                                 'If set, the resulting report will contain section with patients details.')
    @report_api.require_user_login()
    @report_api.response_ok(description='Generates PDF report.')
    @report_api.response_errors(exceptions={NotFoundException}, add_default_namespace_errors=True)
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int], matching_id: int) -> str:
        matchings_below_chosen = request_arg_int(
            MATCHINGS_BELOW_CHOSEN_PARAM,
            minimum=MIN_MATCHINGS_BELOW_CHOSEN,
            maximum=MAX_MATCHINGS_BELOW_CHOSEN
        )
        include_patients_section = request_arg_flag(INCLUDE_PATIENTS_SECTION_PARAM)

        txm_event = get_txm_event_complete(txm_event_id)
        user_id = get_current_user_id()

        configuration = get_configuration_from_db_id_or_default(txm_event, config_id)

        # If configuration not in db yet, save default configuration
        if configuration is None:
            configuration = save_config_parameters_to_db(ConfigParameters(), txm_event.db_id, user_id)

        # Get or solve pairing result
        pairing_result_model = get_pairing_result_comparable_to_config_or_solve(configuration, txm_event)

        directory, report_file_name = generate_pdf_report(
            txm_event,
            configuration.id,
            pairing_result_model,
            matching_id,
            ReportConfiguration(
                matchings_below_chosen,
                include_patients_section
            )
        )

        response = send_from_directory(
            directory,
            report_file_name,
            as_attachment=True,
            download_name=report_file_name,
            max_age=0
        )

        response.headers['x-filename'] = report_file_name
        response.headers['Access-Control-Expose-Headers'] = 'x-filename'
        return response


@report_api.route('/configs/<config_id>/patients/xlsx', methods=['GET'])
class PatientsXLSReport(Resource):

    @report_api.doc(
        params={'config_id': ConfigIdPathParamDefinition},
    )
    @report_api.require_user_login()
    @report_api.response_ok(description='Generates XLSX report.')
    @report_api.response_errors(exceptions={NotFoundException}, add_default_namespace_errors=True)
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)

        configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event=txm_event,
                                                                                      configuration_db_id=config_id)

        patients_dto = to_lists_for_fe(txm_event, configuration_parameters)

        xls_file_name = f'patients_{get_formatted_now()}.xlsx'
        buffer = export_patients_to_xlsx_file(patients_dto)

        response = send_file(
            buffer,
            as_attachment=True,
            download_name=xls_file_name,
            max_age=0
        )

        response.headers['x-filename'] = xls_file_name
        response.headers['Access-Control-Expose-Headers'] = 'x-filename'
        return response
