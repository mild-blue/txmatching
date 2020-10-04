# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class
import datetime
import logging
import os
import time
from typing import List

import jinja2
import pdfkit
from flask import request, send_from_directory
from flask_restx import Resource, abort
from jinja2 import Environment, FileSystemLoader

from txmatching.auth.user.user_auth_check import require_user_edit_access
from txmatching.configuration.subclasses import (ForbiddenCountryCombination,
                                                 ManualDonorRecipientScore)
from txmatching.data_transfer_objects.matchings.matching_dto import (
    CountryDTO, MatchingReportDTO, RoundReportDTO, TransplantDTO)
from txmatching.database.services.config_service import \
    latest_configuration_for_txm_event
from txmatching.database.services.matching_service import \
    get_latest_matchings_and_score_matrix
from txmatching.database.services.txm_event_service import \
    get_txm_event_for_current_user
from txmatching.patients.patient_parameters import HLAAntibodies
from txmatching.utils.blood_groups import ANTIBODIES_MULTIPLIERS_STR, HLATypes
from txmatching.web.api.namespaces import report_api

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = '/tmp/txmatching_reports'


# pylint: disable=no-self-use
# Query params:
#   - matchingRangeLimit
@report_api.route('/<matching_id>', methods=['GET'])
class Report(Resource):

    @report_api.doc(
        security='bearer',
        params={
            'matchingRangeLimit': {
                'description': 'Range limit over/under of requested matching score.',
                'in': 'query',
                'type': 'integer',
                'required': 'true'
            }
        },
        responses={
            200: 'Returns matching report as PDF file.',
            400: 'Raised in case of bad request.',
            404: 'Raised when matching with particular id was not found.'
        }
    )
    @require_user_edit_access()
    # pylint: disable=too-many-locals
    def get(self, matching_id: int) -> str:
        txm_event_id = get_txm_event_for_current_user()
        matching_id = int(request.view_args['matching_id'])
        if request.args.get('matchingRangeLimit') is None or request.args.get('matchingRangeLimit') == '':
            abort(400, "Query argument 'matchingRangeLimit' must be set.")

        matching_range_limit = int(request.args.get('matchingRangeLimit'))
        (all_matchings, score_dict, compatible_blood_dict) = get_latest_matchings_and_score_matrix(txm_event_id)

        requested_matching = list(filter(lambda matching: matching.db_id() == matching_id, all_matchings))
        if len(requested_matching) == 0:
            abort(404, f'Matching with id {matching_id} not found.')

        matching_score = requested_matching[0].score()

        matchings_over_score = list(
            filter(lambda matching: matching.db_id() != matching_id and matching.score() >= matching_score,
                   all_matchings))[
                               :matching_range_limit]
        matchings_under_score = list(
            filter(lambda matching: matching.db_id() != matching_id and matching.score() < matching_score,
                   all_matchings))[
                                :matching_range_limit]
        matchings = requested_matching + matchings_over_score + matchings_under_score

        matching_dtos = [MatchingReportDTO(
            rounds=[
                RoundReportDTO(
                    transplants=[
                        TransplantDTO(
                            score_dict[(donor.db_id, recipient.db_id)],
                            compatible_blood_dict[(donor.db_id, recipient.db_id)],
                            donor,
                            recipient) for donor, recipient in matching_round.donor_recipient_list])
                for matching_round in matching.get_rounds()],
            countries=matching.get_country_codes_counts(),
            score=matching.score(),
            db_id=matching.db_id()
        ) for matching in matchings
        ]

        configuration = latest_configuration_for_txm_event(txm_event_db_id=txm_event_id)

        Report.prepare_tmp_dir()
        Report.prune_old_reports()

        j2_env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, '../templates')),
                             trim_blocks=True)

        now = datetime.datetime.now()
        now_formatted = now.strftime('%Y_%m_%d_%H_%M_%S')

        html = (j2_env.get_template('report.html').render(
            title='Matching Report',
            date=now.strftime('%d.%m.%Y %H:%M:%S'),
            configuration=configuration,
            matchings=matching_dtos
        ))

        html_file_full_path = os.path.join(TMP_DIR, f'report_{now_formatted}.html')
        pdf_file_name = f'report_{now_formatted}.pdf'
        pdf_file_full_path = os.path.join(TMP_DIR, pdf_file_name)

        with open(html_file_full_path, 'w') as text_file:
            text_file.write(html)

        pdfkit.from_file(html_file_full_path, pdf_file_full_path)
        if os.path.exists(html_file_full_path):
            os.remove(html_file_full_path)

        return send_from_directory(TMP_DIR, pdf_file_name, as_attachment=True)

    @staticmethod
    def prepare_tmp_dir():
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

    @staticmethod
    def prune_old_reports():
        now = time.time()
        for filename in os.listdir(TMP_DIR):
            if os.path.getmtime(os.path.join(TMP_DIR, filename)) < now - 1 * 86400:  # 1 day
                if os.path.isfile(os.path.join(TMP_DIR, filename)):
                    print(filename)
                    os.remove(os.path.join(TMP_DIR, filename))


def country_combination_filter(country_combination: ForbiddenCountryCombination) -> str:
    return f'{country_combination.donor_country} - {country_combination.recipient_country}'


def donor_recipient_score_filter(donor_recipient_score: ManualDonorRecipientScore) -> str:
    return f'Donor ({donor_recipient_score.donor_db_id}) - ' \
           f'Recipient ({donor_recipient_score.recipient_db_id}) : {donor_recipient_score.score}'


def antigen_a_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.A.value), codes))


def antigen_b_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.B.value), codes))


def antigen_dr_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(HLATypes.DR.value), codes))


def antibody_a_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.A.value), antibodies.hla_codes_over_cutoff))]


def antibody_b_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.B.value), antibodies.hla_codes_over_cutoff))]


def antibody_dr_filter(antibodies: HLAAntibodies) -> List[str]:
    return [code for code in
            list(filter(lambda x: x.upper().startswith(HLATypes.DR.value), antibodies.hla_codes_over_cutoff))]


def matching_hla_typing_filter(transplant: TransplantDTO) -> List[str]:
    donor_hla_typing = transplant.donor.parameters.hla_typing.codes
    recipient_hla_typing = transplant.recipient.parameters.hla_typing.codes
    return list(set(donor_hla_typing) & set(recipient_hla_typing))


def antigen_score(donor_recipient: TransplantDTO, antigen: HLATypes) -> int:
    filtered = list(
        filter(lambda x: x.upper().startswith(antigen.upper()), matching_hla_typing_filter(donor_recipient)))
    return len(filtered) * ANTIBODIES_MULTIPLIERS_STR[antigen.upper()]


def antigen_score_a_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.A.value)


def antigen_score_b_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.B.value)


def antigen_score_dr_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, HLATypes.DR.value)


def code_from_country_filter(countries: List[CountryDTO]) -> List[str]:
    return [country.country_code for country in countries]


jinja2.filters.FILTERS['country_combination_filter'] = country_combination_filter
jinja2.filters.FILTERS['donor_recipient_score_filter'] = donor_recipient_score_filter
jinja2.filters.FILTERS['antigen_a_filter'] = antigen_a_filter
jinja2.filters.FILTERS['antigen_b_filter'] = antigen_b_filter
jinja2.filters.FILTERS['antigen_dr_filter'] = antigen_dr_filter
jinja2.filters.FILTERS['matching_hla_typing_filter'] = matching_hla_typing_filter
jinja2.filters.FILTERS['antigen_score_a_filter'] = antigen_score_a_filter
jinja2.filters.FILTERS['antigen_score_b_filter'] = antigen_score_b_filter
jinja2.filters.FILTERS['antigen_score_dr_filter'] = antigen_score_dr_filter
jinja2.filters.FILTERS['code_from_country_filter'] = code_from_country_filter
jinja2.filters.FILTERS['antibody_a_filter'] = antibody_a_filter
jinja2.filters.FILTERS['antibody_b_filter'] = antibody_b_filter
jinja2.filters.FILTERS['antibody_dr_filter'] = antibody_dr_filter
