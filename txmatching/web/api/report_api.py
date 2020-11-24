# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import datetime
import logging
import os
import time
from distutils.dir_util import copy_tree
from typing import List, Tuple

import jinja2
import pdfkit
from flask import request, send_from_directory
from flask_restx import Resource
from jinja2 import Environment, FileSystemLoader

from txmatching.auth.exceptions import (InvalidArgumentException,
                                        NotFoundException)
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration, \
    ApplicationEnvironment
from txmatching.configuration.configuration import Configuration
from txmatching.configuration.subclasses import ForbiddenCountryCombination
from txmatching.data_transfer_objects.matchings.matching_dto import (
    CountryDTO, MatchingReportDTO, RoundReportDTO, TransplantDTO)
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import (
    get_config_model_for_txm_event, get_configuration_for_txm_event)
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.services.txm_event_service import \
    get_txm_event_id_for_current_user
from txmatching.patients.patient_parameters import HLAAntibodies
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import HLA_TYPING_BONUS_PER_GENE_CODE_STR, HLATypes
from txmatching.web.api.namespaces import report_api

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = '/tmp/txmatching_reports'
MATCHINGS_BELOW_CHOSEN = 'matchingsBelowChosen'
MIN_MATCHINGS_BELOW_CHOSEN = 0
MAX_MATCHINGS_BELOW_CHOSEN = 20

LOGO_IKEM = './assets/logo_ikem.svg'
COLOR_IKEM = '#e2001a'

LOGO_MILD_BLUE = './assets/logo_mild_blue.svg'
COLOR_MILD_BLUE = '#2D4496'


# Query params:
#   - matchingRangeLimit
@report_api.route('/<matching_id>', methods=['GET'])
class Report(Resource):

    @report_api.doc(
        security='bearer',
        params={
            MATCHINGS_BELOW_CHOSEN: {
                'description': 'Number of matchings with lower score than chosen to include in report',
                'type': int,
                'required': True
            },
            'matching_id': {
                'description': 'Id of matching that was chosen',
                'type': int,
                'in': 'path',
                'required': True
            }
        }
    )
    @report_api.response(code=200, model=None, description='Generates PDF report.')
    @report_api.response(code=404, model=FailJson, description='Matching for provided id was not found')
    @report_api.response(code=401, model=FailJson, description='Authentication failed.')
    @report_api.response(code=403, model=FailJson,
                         description='Access denied. You do not have rights to access this endpoint.'
                         )
    @report_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    # pylint: disable=too-many-locals
    def get(self, matching_id: int) -> str:
        txm_event_db_id = get_txm_event_id_for_current_user()
        txm_event = get_txm_event(txm_event_db_id)
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
        maybe_config_model = get_config_model_for_txm_event(txm_event_db_id)
        if maybe_config_model is None:
            pairing_result = solve_from_configuration(Configuration(), txm_event_db_id=txm_event_db_id)
            solver_service.save_pairing_result(pairing_result)
        (all_matchings, score_dict, compatible_blood_dict) = get_latest_matchings_and_score_matrix(txm_event_db_id)
        all_matchings.sort(key=lambda m: m.order_id())  # lower ID -> better evaluation

        requested_matching = list(filter(lambda matching: matching.order_id() == matching_id, all_matchings))
        if len(requested_matching) == 0:
            raise NotFoundException(f'Matching with id {matching_id} not found.')

        matchings_over = list(
            filter(lambda matching: matching.order_id() < matching_id,
                   all_matchings))
        matchings_under = list(
            filter(lambda matching: matching.order_id() > matching_id,
                   all_matchings))[:matching_range_limit]
        other_matchings_to_include = matchings_over + matchings_under
        other_matchings_to_include.sort(key=lambda m: m.order_id())
        matchings = requested_matching + other_matchings_to_include

        matching_dtos = [MatchingReportDTO(
            rounds=[
                RoundReportDTO(
                    transplants=[
                        TransplantDTO(
                            score_dict[(pair.donor.db_id, pair.recipient.db_id)],
                            compatible_blood_dict[(pair.donor.db_id, pair.recipient.db_id)],
                            pair.donor,
                            pair.recipient) for pair in matching_round.donor_recipient_pairs])
                for matching_round in matching.get_rounds()],
            countries=matching.get_country_codes_counts(),
            score=matching.score(),
            order_id=matching.order_id()
        ) for matching in matchings
        ]

        configuration = get_configuration_for_txm_event(txm_event_db_id=txm_event_db_id)

        Report.prepare_tmp_dir()
        Report.copy_assets()
        Report.prune_old_reports()

        j2_env = Environment(
            loader=FileSystemLoader(os.path.join(THIS_DIR, '../templates')),
            trim_blocks=True
        )

        now = datetime.datetime.now()
        now_formatted = now.strftime('%Y_%m_%d_%H_%M_%S')

        required_patients_medical_ids = [txm_event.active_recipients_dict[recipient_db_id].medical_id
                                         for recipient_db_id in configuration.required_patient_db_ids]

        manual_donor_recipient_scores_with_medical_ids = [
            (
                txm_event.active_donors_dict[donor_recipient_score.donor_db_id].medical_id,
                txm_event.active_recipients_dict[donor_recipient_score.recipient_db_id].medical_id,
                donor_recipient_score.score
            ) for donor_recipient_score in
            configuration.manual_donor_recipient_scores
        ]

        logo, color = Report.get_theme()
        html = (j2_env.get_template('report.html').render(
            title='Matching Report',
            date=now.strftime('%d.%m.%Y %H:%M:%S'),
            configuration=configuration,
            matchings=matching_dtos,
            required_patients_medical_ids=required_patients_medical_ids,
            manual_donor_recipient_scores_with_medical_ids=manual_donor_recipient_scores_with_medical_ids,
            logo=logo,
            color=color
        ))

        html_file_full_path = os.path.join(TMP_DIR, f'report_{now_formatted}.html')
        pdf_file_name = f'report_{now_formatted}.pdf'
        pdf_file_full_path = os.path.join(TMP_DIR, pdf_file_name)

        with open(html_file_full_path, 'w') as text_file:
            text_file.write(html)

        pdfkit.from_file(
            input=html_file_full_path,
            output_path=pdf_file_full_path,
            options={
                'footer-center': '[page] / [topage]',
                'enable-local-file-access': '',
                '--margin-top': '0',
                '--margin-left': '0',
                '--margin-right': '0',
                '--margin-bottom': '0',
            }
        )
        if os.path.exists(html_file_full_path):
            os.remove(html_file_full_path)

        response = send_from_directory(
            TMP_DIR,
            pdf_file_name,
            as_attachment=True,
            attachment_filename=pdf_file_name,
            cache_timeout=0
        )

        response.headers['x-filename'] = pdf_file_name
        response.headers['Access-Control-Expose-Headers'] = 'x-filename'
        return response

    @staticmethod
    def prepare_tmp_dir():
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

    @staticmethod
    def copy_assets():
        if os.path.exists(TMP_DIR):
            old_dir = os.path.join(THIS_DIR, '../templates/assets/')
            new_dir = TMP_DIR + '/assets/'
            copy_tree(old_dir, new_dir)

    @staticmethod
    def prune_old_reports():
        now = time.time()
        for filename in os.listdir(TMP_DIR):
            if os.path.getmtime(os.path.join(TMP_DIR, filename)) < now - 1 * 86400:  # 1 day
                if os.path.isfile(os.path.join(TMP_DIR, filename)):
                    print(filename)
                    os.remove(os.path.join(TMP_DIR, filename))

    @staticmethod
    def get_theme() -> Tuple[str, str]:
        conf = get_application_configuration()
        return (LOGO_MILD_BLUE, COLOR_MILD_BLUE) if conf.environment == ApplicationEnvironment.STAGING \
            else (LOGO_IKEM, COLOR_IKEM)


def country_combination_filter(country_combination: ForbiddenCountryCombination) -> str:
    return f'{country_combination.donor_country} - {country_combination.recipient_country}'


def donor_recipient_score_filter(donor_recipient_score: Tuple) -> str:
    return f'{donor_recipient_score[0]} -> {donor_recipient_score[1]} : {donor_recipient_score[2]}'


def antigen_a_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.A.value), codes))


def antigen_b_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.B.value), codes))


def antigen_dr_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.DR.value), codes))


def _start_with(value: str, values: List[str]) -> bool:
    for val in values:
        if value.upper().startswith(val):
            return True
    return False


def antigen_other_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: not _start_with(x, [hla.value for hla in HLATypes]), codes))


def antibody_a_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.A.value), antibodies.hla_codes_over_cutoff))]


def antibody_b_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.B.value), antibodies.hla_codes_over_cutoff))]


def antibody_dr_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.DR.value), antibodies.hla_codes_over_cutoff))]


def antibody_other_filter(antibodies: HLAAntibodies) -> List[str]:
    return list(filter(lambda x: not _start_with(x, [hla.value for hla in HLATypes]), antibodies.hla_codes_over_cutoff))


def matching_hla_typing_filter(transplant: TransplantDTO) -> List[str]:
    donor_hla_typing = transplant.donor.parameters.hla_typing.codes
    recipient_hla_typing = transplant.recipient.parameters.hla_typing.codes
    return list(set(donor_hla_typing) & set(recipient_hla_typing))


def antigen_score(donor_recipient: TransplantDTO, antigen: HLATypes) -> int:
    filtered = list(
        filter(lambda x: x.upper().startswith(antigen.upper()), matching_hla_typing_filter(donor_recipient)))
    return len(filtered) * HLA_TYPING_BONUS_PER_GENE_CODE_STR[antigen.upper()]


def antigen_score_a_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.A.value)


def antigen_score_b_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.B.value)


def antigen_score_dr_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.DR.value)


def code_from_country_filter(countries: List[CountryDTO]) -> List[str]:
    return [country.country_code.value for country in countries]


def sum_of_transplants(matching: MatchingReportDTO) -> int:
    count_of_transplants = 0
    for matching_round in matching.rounds:
        count_of_transplants += len(matching_round.transplants)
    return count_of_transplants


jinja2.filters.FILTERS['country_combination_filter'] = country_combination_filter
jinja2.filters.FILTERS['donor_recipient_score_filter'] = donor_recipient_score_filter
jinja2.filters.FILTERS['antigen_a_filter'] = antigen_a_filter
jinja2.filters.FILTERS['antigen_b_filter'] = antigen_b_filter
jinja2.filters.FILTERS['antigen_dr_filter'] = antigen_dr_filter
jinja2.filters.FILTERS['antigen_other_filter'] = antigen_other_filter
jinja2.filters.FILTERS['matching_hla_typing_filter'] = matching_hla_typing_filter
jinja2.filters.FILTERS['antigen_score_a_filter'] = antigen_score_a_filter
jinja2.filters.FILTERS['antigen_score_b_filter'] = antigen_score_b_filter
jinja2.filters.FILTERS['antigen_score_dr_filter'] = antigen_score_dr_filter
jinja2.filters.FILTERS['code_from_country_filter'] = code_from_country_filter
jinja2.filters.FILTERS['antibody_a_filter'] = antibody_a_filter
jinja2.filters.FILTERS['antibody_b_filter'] = antibody_b_filter
jinja2.filters.FILTERS['antibody_dr_filter'] = antibody_dr_filter
jinja2.filters.FILTERS['antibody_other_filter'] = antibody_other_filter
jinja2.filters.FILTERS['sum_of_transplants'] = sum_of_transplants
