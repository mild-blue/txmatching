# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import logging
from typing import Optional

from flask import request, send_file, send_from_directory
from flask_restx import Resource

from txmatching.auth.auth_check import (require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigIdPathParamDefinition
from txmatching.data_transfer_objects.patients.out_dtos.conversions import \
    to_lists_for_fe
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import (
    find_config_db_id_for_configuration_and_data,
    get_configuration_from_db_id_or_default)
from txmatching.database.services.report_service import (
    ReportConfiguration, export_patients_to_xlsx_file, generate_html_report,
    generate_pdf_report)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
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
            MATCHINGS_BELOW_CHOSEN_PARAM: {
                'description': 'Number of matchings with lower score than chosen to include in report.',
                'type': int,
                'required': True
            },
            INCLUDE_PATIENTS_SECTION_PARAM: {
                'description': 'If set to true, the resulting report will contain section with patients details..',
                'type': bool,
                'required': False
            },
            'matching_id': {
                'description': 'Id of matching that was chosen',
                'type': int,
                'in': 'path',
                'required': True
            },
            'config_id': ConfigIdPathParamDefinition
        }
    )
    @report_api.require_user_login()
    @report_api.response_ok(description='Generates PDF report.')
    @report_api.response_error_matching_not_found()
    @report_api.response_errors()
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

        configuration = get_configuration_from_db_id_or_default(txm_event, configuration_db_id=config_id)
        maybe_configuration_db_id = find_config_db_id_for_configuration_and_data(txm_event=txm_event,
                                                                                 configuration=configuration)

        if maybe_configuration_db_id is None:
            pairing_result = solve_from_configuration(configuration, txm_event=txm_event)
            user_id = get_current_user_id()
            solver_service.save_pairing_result(pairing_result, user_id)
            maybe_configuration_db_id = find_config_db_id_for_configuration_and_data(txm_event=txm_event,
                                                                                     configuration=configuration)

        assert maybe_configuration_db_id is not None

        directory, report_file_name = generate_pdf_report(
            txm_event,
            maybe_configuration_db_id,
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
            attachment_filename=report_file_name,
            cache_timeout=0
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
    @report_api.response_error_matching_not_found()
    @report_api.response_errors()
    @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)

        configuration = get_configuration_from_db_id_or_default(txm_event=txm_event,
                                                                configuration_db_id=config_id)

        patients_dto = to_lists_for_fe(txm_event, configuration)

        xls_file_name = f'patients_{get_formatted_now()}.xlsx'
        buffer = export_patients_to_xlsx_file(patients_dto)

        response = send_file(
            buffer,
            as_attachment=True,
            attachment_filename=xls_file_name,
            cache_timeout=0
        )

        response.headers['x-filename'] = xls_file_name
        response.headers['Access-Control-Expose-Headers'] = 'x-filename'
        return response
