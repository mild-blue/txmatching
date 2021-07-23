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
    export_patients_to_xlsx_file, generate_pdf_report)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.logged_user import get_current_user_id
from txmatching.utils.time import get_formatted_now
from txmatching.web.web_utils.namespaces import report_api

logger = logging.getLogger(__name__)

MATCHINGS_BELOW_CHOSEN = 'matchingsBelowChosen'
MIN_MATCHINGS_BELOW_CHOSEN = 0
MAX_MATCHINGS_BELOW_CHOSEN = 20


# Query params:
#   - matchingRangeLimit
@report_api.route('/configs/<config_id>/matchings/<int:matching_id>/pdf', methods=['GET'])
class MatchingReport(Resource):

    @report_api.doc(
        params={
            MATCHINGS_BELOW_CHOSEN: {
                'description': 'Number of matchings with lower score than chosen to include in report.',
                'type': int,
                'required': True
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

        matching_id = int(request.view_args['matching_id'])
        if request.args.get(MATCHINGS_BELOW_CHOSEN) is None or request.args.get(MATCHINGS_BELOW_CHOSEN) == '':
            raise InvalidArgumentException(f'Query argument {MATCHINGS_BELOW_CHOSEN} must be set.')

        matching_range_limit = int(request.args.get(MATCHINGS_BELOW_CHOSEN))

        if matching_range_limit < MIN_MATCHINGS_BELOW_CHOSEN or matching_range_limit > MAX_MATCHINGS_BELOW_CHOSEN:
            raise InvalidArgumentException(
                f'Query argument {MATCHINGS_BELOW_CHOSEN} must be in '
                f'range [{MIN_MATCHINGS_BELOW_CHOSEN}, {MAX_MATCHINGS_BELOW_CHOSEN}]. '
                f'Current value is {matching_range_limit}.'
            )

        directory, pdf_file_name = generate_pdf_report(
            txm_event,
            maybe_configuration_db_id,
            matching_id,
            matching_range_limit
        )

        response = send_from_directory(
            directory,
            pdf_file_name,
            as_attachment=True,
            attachment_filename=pdf_file_name,
            cache_timeout=0
        )

        response.headers['x-filename'] = pdf_file_name
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
