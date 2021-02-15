# pylint: disable=no-self-use
# Can not, the methods here need self due to the annotations. They are used for generating swagger which needs class.
import datetime
import itertools
import logging
import os
import time
from dataclasses import dataclass, replace
from distutils.dir_util import copy_tree
from typing import Dict, List, Optional, Tuple, Union

import jinja2
import pandas as pd
import pdfkit
from flask import request, send_from_directory
from flask_restx import Resource
from jinja2 import Environment, FileSystemLoader

from txmatching.auth.auth_check import require_valid_txm_event_id
from txmatching.auth.exceptions import (InvalidArgumentException,
                                        NotFoundException)
from txmatching.auth.user.user_auth_check import require_user_login
from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationEnvironment, get_application_configuration)
from txmatching.configuration.configuration import Configuration
from txmatching.configuration.subclasses import ForbiddenCountryCombination
from txmatching.data_transfer_objects.matchings.matching_dto import (
    CountryDTO, RoundDTO)
from txmatching.data_transfer_objects.patients.out_dots.conversions import \
    to_lists_for_fe
from txmatching.data_transfer_objects.patients.out_dots.donor_dto_out import \
    DonorDTOOut
from txmatching.data_transfer_objects.txm_event.txm_event_swagger import \
    FailJson
from txmatching.database.services import solver_service
from txmatching.database.services.config_service import (
    find_configuration_db_id_for_configuration,
    get_latest_configuration_db_id_for_txm_event,
    get_latest_configuration_for_txm_event)
from txmatching.database.services.matching_service import (
    create_calculated_matchings_dto, get_matchings_detailed_for_configuration)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.patients.hla_model import HLAAntibody, HLAType
from txmatching.patients.patient import Donor, DonorType, Patient, Recipient
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.logged_user import get_current_user_id
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
@report_api.route('/<int:matching_id>', methods=['GET'])
class Report(Resource):

    @report_api.doc(
        security='bearer',
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
            }
        }
    )
    @report_api.response(code=200, model=None, description='Generates PDF report.')
    @report_api.response(code=404, model=FailJson, description='Matching for provided id was not found.')
    @report_api.response(code=401, model=FailJson, description='Authentication failed.')
    @report_api.response(code=403, model=FailJson,
                         description='Access denied. You do not have rights to access this endpoint.'
                         )
    @report_api.response(code=500, model=FailJson, description='Unexpected error, see contents for details.')
    @require_user_login()
    @require_valid_txm_event_id()
    # pylint: disable=too-many-locals
    def get(self, txm_event_id: int, matching_id: int) -> str:
        txm_event = get_txm_event_complete(txm_event_id)
        maybe_configuration_db_id = get_latest_configuration_db_id_for_txm_event(txm_event)

        if maybe_configuration_db_id is None:
            configuration = Configuration()
            pairing_result = solve_from_configuration(configuration, txm_event=txm_event)
            user_id = get_current_user_id()
            solver_service.save_pairing_result(pairing_result, user_id)
            maybe_configuration_db_id = find_configuration_db_id_for_configuration(txm_event=txm_event,
                                                                                   configuration=configuration)

        assert maybe_configuration_db_id is not None

        latest_matchings_detailed = get_matchings_detailed_for_configuration(txm_event, maybe_configuration_db_id)

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

        # lower ID -> better evaluation
        sorted_matchings = sorted(latest_matchings_detailed.matchings, key=lambda m: m.order_id())

        requested_matching = list(filter(lambda matching: matching.order_id() == matching_id, sorted_matchings))
        if len(requested_matching) == 0:
            raise NotFoundException(f'Matching with id {matching_id} not found.')

        other_matchings_to_include = list(
            itertools.islice(
                filter(
                    lambda matching: matching.order_id() != matching_id,
                    sorted_matchings
                ),
                matching_range_limit
            )
        )

        matchings = requested_matching + other_matchings_to_include

        calculated_matchings_dto = create_calculated_matchings_dto(latest_matchings_detailed, matchings)

        patients_dto = to_lists_for_fe(txm_event)

        configuration = get_latest_configuration_for_txm_event(txm_event=txm_event)

        Report.prepare_tmp_dir()
        Report.copy_assets()
        Report.prune_old_reports()

        j2_env = Environment(
            loader=FileSystemLoader(os.path.join(THIS_DIR, '../templates')),
            trim_blocks=True
        )

        now = datetime.datetime.now()
        now_formatted = now.strftime('%Y_%m_%d_%H_%M_%S')

        # Uncomment to export patients to xlsx file
        # xls_file_full_path = os.path.join(TMP_DIR, f'patients_{now_formatted}.xlsx')
        # export_patients_to_xlsx_file(patients_dto, xls_file_full_path)

        required_patients_medical_ids = [txm_event.active_recipients_dict[recipient_db_id].medical_id
                                         for recipient_db_id in configuration.required_patient_db_ids]

        manual_donor_recipient_scores_with_medical_ids = [
            (
                next(
                    donor for donor in txm_event.all_donors
                    if donor.db_id == donor_recipient_score.donor_db_id
                ).medical_id,
                next(
                    recipient for recipient in txm_event.all_recipients
                    if recipient.db_id == donor_recipient_score.recipient_db_id
                ).medical_id,
                donor_recipient_score.score
            ) for donor_recipient_score in
            configuration.manual_donor_recipient_scores
        ]

        logo, color = Report.get_theme()
        html = (j2_env.get_template('report.html').render(
            title='Matching Report',
            date=now.strftime('%d.%m.%Y %H:%M:%S'),
            txm_event_name=txm_event.name,
            configuration=configuration,
            matchings=calculated_matchings_dto,
            patients=patients_dto,
            required_patients_medical_ids=required_patients_medical_ids,
            manual_donor_recipient_scores_with_medical_ids=manual_donor_recipient_scores_with_medical_ids,
            all_donors={donor.medical_id: donor for donor in txm_event.all_donors},
            all_recipients={recipient.medical_id: recipient for recipient in txm_event.all_recipients},
            all_recipients_by_db_id={recipient.db_id: recipient for recipient in txm_event.all_recipients},
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
                    os.remove(os.path.join(TMP_DIR, filename))

    @staticmethod
    def get_theme() -> Tuple[str, str]:
        conf = get_application_configuration()
        return (LOGO_MILD_BLUE, COLOR_MILD_BLUE) if conf.environment == ApplicationEnvironment.STAGING \
            else (LOGO_IKEM, COLOR_IKEM)


def export_patients_to_xlsx_file(patients_dto: Dict[str, Union[List[DonorDTOOut], List[Recipient]]], output_file: str):
    @dataclass
    class PatientPair:
        # pylint: disable=too-many-instance-attributes
        donor_medical_id: str
        donor_country: str
        donor_height: int
        donor_weight: float
        donor_sex: str
        donor_year_of_birth: int
        donor_blood_group: str
        donor_type: str
        donor_antigens: str
        recipient_medical_id: str = ''
        recipient_country: str = ''
        recipient_height: int = None
        recipient_weight: float = None
        recipient_sex: str = ''
        recipient_year_of_birth: int = None
        recipient_blood_group: str = ''
        recipient_acceptable_blood_groups: str = ''
        recipient_antigens: str = ''
        recipient_antibodies: str = ''

    all_recipients_by_db_id = {recipient.db_id: recipient for recipient in patients_dto['recipients']}

    patient_pairs = []
    for donor in patients_dto['donors']:  # type: Donor
        recipient = (
            all_recipients_by_db_id[donor.related_recipient_db_id] if donor.related_recipient_db_id else None
        )  # type: Recipient

        patient_pair = PatientPair(
            donor_medical_id=donor.medical_id,
            donor_country=donor.parameters.country_code.value,
            donor_height=donor.parameters.height,
            donor_weight=donor.parameters.weight,
            donor_sex=donor.parameters.sex.value if donor.parameters.sex is not None else '',
            donor_year_of_birth=donor.parameters.year_of_birth,
            donor_blood_group=donor.parameters.blood_group,
            donor_type=donor_type_label_filter(donor.donor_type),
            donor_antigens=' '.join([hla.raw_code for hla in donor.parameters.hla_typing.hla_types_list]),
        )
        if recipient is not None:
            antibodies: List[HLAAntibody] = []
            for antibodies_per_group in recipient.hla_antibodies.hla_antibodies_per_groups:
                antibodies.extend(antibodies_per_group.hla_antibody_list)

            patient_pair = replace(
                patient_pair,
                recipient_medical_id=recipient.medical_id,
                recipient_country=recipient.parameters.country_code.value,
                recipient_height=recipient.parameters.height,
                recipient_weight=recipient.parameters.weight,
                recipient_sex=recipient.parameters.sex.value if recipient.parameters.sex is not None else '',
                recipient_year_of_birth=recipient.parameters.year_of_birth,
                recipient_blood_group=recipient.parameters.blood_group,
                recipient_acceptable_blood_groups=(
                    ', '.join([blood_group for blood_group in recipient.acceptable_blood_groups])
                ),
                recipient_antigens=' '.join([hla.raw_code for hla in recipient.parameters.hla_typing.hla_types_list]),
                recipient_antibodies=' '.join([antibody.raw_code for antibody in antibodies]),
            )
        patient_pairs.append(patient_pair)

    df_with_patients = pd.DataFrame(patient_pairs)

    # Save to xls file and set some formatting
    # pylint: disable=abstract-class-instantiated
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df_with_patients.to_excel(writer, sheet_name='Patients', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Patients']
    # wrap text in the cells
    workbook_format = workbook.add_format({'text_wrap': True})
    # increase columns width to 20
    worksheet.set_column('A:S', 20, workbook_format)
    writer.save()


def country_combination_filter(country_combination: ForbiddenCountryCombination) -> str:
    return f'{country_combination.donor_country} - {country_combination.recipient_country}'


def donor_recipient_score_filter(donor_recipient_score: Tuple) -> str:
    return f'{donor_recipient_score[0]} -> {donor_recipient_score[1]} : {donor_recipient_score[2]}'


def country_code_from_country_filter(countries: List[CountryDTO]) -> List[str]:
    return [country.country_code.value for country in countries]


def patient_by_medical_id_filter(medical_id: str, patients: Dict[str, Patient]) -> Patient:
    return patients[medical_id]


def patient_height_and_weight_filter(patient: Patient) -> Optional[str]:
    height = patient.parameters.height
    weight = patient.parameters.weight

    if height is not None and weight is not None:
        return f'{height}/{weight:.0f}'
    elif height is not None:
        return f'{height}/-'
    elif weight is not None:
        return f'-/{weight:.0f}'
    else:
        return None


def score_color_filter(score: Optional[float], configuration: Configuration):
    # wkhtmltopdf does not support linear-gradients css style that is used in fe and makes
    # exporting super-slow so we define percentage->color mapping in this function

    if score is None:
        percentage = 0
    elif score == -1:
        return '#ff0000'  # bad-matching
    else:
        percentage = 100 * score / configuration.maximum_total_score

    if percentage < 15:
        return '#ffa400'
    elif percentage < 30:
        return '#ffe14c'
    elif percentage < 75:
        return '#cfe733'
    elif percentage < 100:
        return '#98d961'
    else:
        return '#70c47b'


def _get_donor_type_from_round(matching_round: RoundDTO, donors: Dict[str, Donor]) -> Optional[DonorType]:
    if len(matching_round.transplants) == 0:
        return None

    donor_id = matching_round.transplants[0].donor
    return donors[donor_id].donor_type


def donor_type_label_filter(donor_type: DonorType) -> str:
    if donor_type == DonorType.BRIDGING_DONOR:
        return 'bridging donor'
    elif donor_type == DonorType.NON_DIRECTED:
        return 'non-directed donor'
    else:
        return ''


def donor_type_label_from_round_filter(matching_round: RoundDTO, donors: Dict[str, Donor]) -> str:
    donor_type = _get_donor_type_from_round(matching_round, donors)
    return donor_type_label_filter(donor_type)


def round_index_from_order_filter(order: int, matching_round: RoundDTO, donors: Dict[str, Donor]) -> str:
    donor_type = _get_donor_type_from_round(matching_round, donors)

    if donor_type == DonorType.BRIDGING_DONOR:
        return f'{order}B'
    elif donor_type == DonorType.NON_DIRECTED:
        return f'{order}N'
    else:
        return f'{order}'


def hla_type_filter(hla: Union[HLAType, HLAAntibody]):
    if hla.code == hla.raw_code:
        return f'{hla.code}'
    else:
        return f'{hla.code} ({hla.raw_code})'


jinja2.filters.FILTERS.update({
    'country_combination_filter': country_combination_filter,
    'donor_recipient_score_filter': donor_recipient_score_filter,
    'country_code_from_country_filter': country_code_from_country_filter,
    'patient_by_medical_id_filter': patient_by_medical_id_filter,
    'patient_height_and_weight_filter': patient_height_and_weight_filter,
    'score_color_filter': score_color_filter,
    'donor_type_label_filter': donor_type_label_filter,
    'donor_type_label_from_round_filter': donor_type_label_from_round_filter,
    'round_index_from_order_filter': round_index_from_order_filter,
    'hla_type_filter': hla_type_filter,
})
