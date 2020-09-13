# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class
import datetime
import logging
import os
import time

import jinja2
import pdfkit
from flask import send_from_directory, request
from flask_restx import Resource
from jinja2 import Environment, FileSystemLoader

from txmatching.config.subclasses import ForbiddenCountryCombination, ManualDonorRecipientScore
from txmatching.database.services.config_service import get_current_configuration
from txmatching.database.services.matching_service import get_latest_matchings_and_score_matrix
from txmatching.web.api.namespaces import report_api
from txmatching.web.auth.login_check import login_required

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = "/tmp/txmatching_reports"
MIN_MATCHING_SCORE = 48
MATCHING_RANGE_LIMIT = 5


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@report_api.route('/<matching_id>', methods=['GET'])
class Report(Resource):

    @report_api.doc(security='bearer')
    @report_api.response(code=200, description='')
    @login_required()
    # pylint: disable=too-many-locals
    def get(self, matching_id: str) -> str:
        matching_id = request.view_args['matching_id']
        (all_matchings, _score_dict, _compatible_blood_dict) = get_latest_matchings_and_score_matrix()

        requested_matching = list(filter(lambda x: x.id() == matching_id, all_matchings))
        matchings_over_score = list(
            filter(lambda x: x.id() != matching_id and x.score() >= MIN_MATCHING_SCORE, all_matchings))[
                               :MATCHING_RANGE_LIMIT]
        matchings_under_score = list(
            filter(lambda x: x.id() != matching_id and x.score() < MIN_MATCHING_SCORE, all_matchings))[
                                :MATCHING_RANGE_LIMIT]
        matchings = requested_matching + matchings_over_score + matchings_under_score

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
            matchings=matchings
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


def country_combination_filter(country_combination: ForbiddenCountryCombination):
    return f"{country_combination.donor_country} - {country_combination.recipient_country}"


def donor_recipient_score_filter(donor_recipient_score: ManualDonorRecipientScore):
    return f"Donor ({donor_recipient_score.donor_db_id}) - " \
           f"Recipient ({donor_recipient_score.recipient_db_id}) : {donor_recipient_score.score}"


jinja2.filters.FILTERS["country_combination_filter"] = country_combination_filter
jinja2.filters.FILTERS["donor_recipient_score_filter"] = donor_recipient_score_filter
