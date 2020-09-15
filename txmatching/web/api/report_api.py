# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class
import dataclasses
import datetime
import logging
import os
from typing import List

import time
import jinja2
import pdfkit
from flask import send_from_directory, request
from flask_restx import Resource
from jinja2 import Environment, FileSystemLoader

from txmatching.config.subclasses import ForbiddenCountryCombination, ManualDonorRecipientScore
from txmatching.data_transfer_objects.matchings.matching_dto import TransplantDTO, \
    RoundReportDTO, MatchingReportDTO, CountryDTO
from txmatching.database.services.config_service import get_current_configuration
from txmatching.database.services.matching_service import get_latest_matchings_and_score_matrix
from txmatching.utils.blood_groups import Antigens, ANTIBODIES_MULTIPLIERS_STR
from txmatching.web.api.namespaces import report_api

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = "/tmp/txmatching_reports"

# pylint: disable=no-self-use
# Query params:
#   - matchingRangeLimit
#   - matchingScore
@report_api.route('/<matching_id>', methods=['GET'])
class Report(Resource):

    @report_api.doc(security='bearer')
    @report_api.response(code=200, description='')
    # @login_required()
    # pylint: disable=too-many-locals
    def get(self, matching_id: int) -> str:
        matching_id = request.view_args['matching_id']
        matching_range_limit = int(request.args.get('matchingRangeLimit'))
        matching_score = int(request.args.get('matchingScore'))
        (all_matchings, score_dict, compatible_blood_dict) = get_latest_matchings_and_score_matrix()

        requested_matching = list(filter(lambda x: x.db_id() == matching_id, all_matchings))
        matchings_over_score = list(
            filter(lambda x: x.db_id() != matching_id and x.score() >= matching_score, all_matchings))[
                               :matching_range_limit]
        matchings_under_score = list(
            filter(lambda x: x.db_id() != matching_id and x.score() < matching_score, all_matchings))[
                                :matching_range_limit]
        matchings = requested_matching + matchings_over_score + matchings_under_score

        matching_dtos = [
            dataclasses.asdict(MatchingReportDTO(
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
            )) for matching in matchings
        ]

        configuration = get_current_configuration()

        self.prepare_tmp_dir()
        self.prune_old_reports()

        j2_env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, "../templates")),
                             trim_blocks=True)

        now = datetime.datetime.now()
        now_formatted = now.strftime("%Y_%m_%d_%H_%M_%S")

        html = (j2_env.get_template('report.html').render(
            title="Matching Report",
            date=now.strftime("%d.%m.%Y %H:%M:%S"),
            configuration=configuration,
            matchings=matching_dtos
        ))

        html_file_full_path = os.path.join(TMP_DIR, f"report_{now_formatted}.html")
        pdf_file_name = f"report_{now_formatted}.pdf"
        pdf_file_full_path = os.path.join(TMP_DIR, pdf_file_name)

        with open(html_file_full_path, "w") as text_file:
            text_file.write(html)

        pdfkit.from_file(html_file_full_path, pdf_file_full_path)
        if os.path.exists(html_file_full_path):
            os.remove(html_file_full_path)

        return send_from_directory(TMP_DIR, pdf_file_name, as_attachment=True)

    def prepare_tmp_dir(self):
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

    def prune_old_reports(self):
        now = time.time()
        for filename in os.listdir(TMP_DIR):
            if os.path.getmtime(os.path.join(TMP_DIR, filename)) < now - 1 * 86400:
                if os.path.isfile(os.path.join(TMP_DIR, filename)):
                    print(filename)
                    os.remove(os.path.join(TMP_DIR, filename))


def country_combination_filter(country_combination: ForbiddenCountryCombination) -> str:
    return f"{country_combination.donor_country} - {country_combination.recipient_country}"


def donor_recipient_score_filter(donor_recipient_score: ManualDonorRecipientScore) -> str:
    return f"Donor ({donor_recipient_score.donor_db_id}) - " \
           f"Recipient ({donor_recipient_score.recipient_db_id}) : {donor_recipient_score.score}"


def antigen_a_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(Antigens.A.value), codes))


def antigen_b_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(Antigens.B.value), codes))


def antigen_dr_filter(codes: List[str]) -> List[str]:
    return list(filter(lambda x: x.upper().startswith(Antigens.DR.value), codes))


def matching_antigens_filter(transplant: TransplantDTO) -> List[str]:
    donor_antigens = transplant["donor"]["parameters"]["hla_antigens"]["codes"]
    recipient_antigens = transplant["recipient"]["parameters"]["hla_antigens"]["codes"]
    return list(set(donor_antigens) & set(recipient_antigens))


def antigen_score(donor_recipient: TransplantDTO, antigen: Antigens) -> int:
    filtered = list(filter(lambda x: x.upper().startswith(antigen.upper()), matching_antigens_filter(donor_recipient)))
    return len(filtered) * ANTIBODIES_MULTIPLIERS_STR[antigen.upper()]


def antigen_score_a_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, Antigens.A.value)


def antigen_score_b_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, Antigens.B.value)


def antigen_score_dr_filter(transplant: TransplantDTO) -> int:
    return antigen_score(transplant, Antigens.DR.value)


def code_from_country_filter(countries: List[CountryDTO]) -> List[str]:
    return [country["country_code"] for country in countries]


jinja2.filters.FILTERS["country_combination_filter"] = country_combination_filter
jinja2.filters.FILTERS["donor_recipient_score_filter"] = donor_recipient_score_filter
jinja2.filters.FILTERS["antigen_a_filter"] = antigen_a_filter
jinja2.filters.FILTERS["antigen_b_filter"] = antigen_b_filter
jinja2.filters.FILTERS["antigen_dr_filter"] = antigen_dr_filter
jinja2.filters.FILTERS["matching_antigens_filter"] = matching_antigens_filter
jinja2.filters.FILTERS["antigen_score_a_filter"] = antigen_score_a_filter
jinja2.filters.FILTERS["antigen_score_b_filter"] = antigen_score_b_filter
jinja2.filters.FILTERS["antigen_score_dr_filter"] = antigen_score_dr_filter
jinja2.filters.FILTERS["code_from_country_filter"] = code_from_country_filter
