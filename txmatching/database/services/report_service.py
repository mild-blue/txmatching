import datetime
import itertools
import logging
import os
import time
from dataclasses import dataclass, replace
from distutils.dir_util import copy_tree
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union

import jinja2
import pandas as pd
import pdfkit
from jinja2 import Environment, FileSystemLoader

from txmatching.auth.exceptions import NotFoundException
from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationColourScheme, get_application_configuration)
from txmatching.configuration.subclasses import ForbiddenCountryCombination
from txmatching.data_transfer_objects.matchings.matching_dto import (
    CountryDTO, RoundDTO)
from txmatching.data_transfer_objects.patients.out_dtos.conversions import \
    to_lists_for_fe
from txmatching.data_transfer_objects.patients.out_dtos.donor_dto_out import \
    DonorDTOOut
from txmatching.database.services.config_service import \
    get_configuration_parameters_from_db_id_or_default
from txmatching.database.services.matching_service import (
    create_calculated_matchings_dto,
    get_matchings_detailed_for_pairing_result_model)
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.patients.hla_model import HLAAntibody, HLAType
from txmatching.patients.patient import (Donor, DonorType, Patient, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.utils.time import get_formatted_now

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(THIS_DIR, '../../templates')
TMP_DIR = '/tmp/txmatching_reports'

LOGO_IKEM = './assets/logo_ikem.svg'
COLOR_IKEM = '#e2001a'

LOGO_MILD_BLUE = './assets/logo_mild_blue.svg'
COLOR_MILD_BLUE = '#2D4496'


@dataclass
class ReportConfiguration:
    matchings_below_chosen: int
    include_patients_section: bool


# pylint: disable=too-many-locals
def generate_html_report(
        txm_event: TxmEvent,
        configuration_db_id: int,
        pairing_result_model: PairingResultModel,
        matching_id: int,
        report_config: ReportConfiguration
) -> Tuple[str, str]:
    latest_matchings_detailed = get_matchings_detailed_for_pairing_result_model(pairing_result_model, txm_event)

    # lower ID -> better evaluation
    sorted_matchings = sorted(latest_matchings_detailed.matchings, key=lambda m: m.order_id)

    requested_matching = list(filter(lambda matching: matching.order_id == matching_id, sorted_matchings))
    if len(requested_matching) == 0:
        raise NotFoundException(f'Matching with id {matching_id} not found.')

    other_matchings_to_include = list(
        itertools.islice(
            filter(
                lambda matching: matching.order_id != matching_id,
                sorted_matchings
            ),
            report_config.matchings_below_chosen
        )
    )

    matchings = requested_matching + other_matchings_to_include

    calculated_matchings_dto = create_calculated_matchings_dto(latest_matchings_detailed, matchings,
                                                               configuration_db_id)

    configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event=txm_event,
                                                                                  configuration_db_id=configuration_db_id)

    patients_dto = to_lists_for_fe(txm_event, configuration_parameters)

    _prepare_tmp_dir()
    _copy_assets()
    _prune_old_reports()

    j2_env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True
    )

    required_patients_medical_ids = [txm_event.active_and_valid_recipients_dict[recipient_db_id].medical_id
                                     for recipient_db_id in configuration_parameters.required_patient_db_ids]

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
        configuration_parameters.manual_donor_recipient_scores
    ]

    logo, color = _get_theme()
    html = (j2_env.get_template('report.html').render(
        title='Matching Report',
        date=datetime.datetime.now().strftime('%b %d, %Y %H:%M:%S'),
        txm_event_name=txm_event.name,
        configuration=configuration_parameters,
        matchings=calculated_matchings_dto,
        patients=patients_dto,
        required_patients_medical_ids=required_patients_medical_ids,
        manual_donor_recipient_scores_with_medical_ids=manual_donor_recipient_scores_with_medical_ids,
        all_donors={donor.medical_id: donor for donor in txm_event.all_donors},
        all_recipients={recipient.medical_id: recipient for recipient in txm_event.all_recipients},
        all_recipients_by_db_id={recipient.db_id: recipient for recipient in txm_event.all_recipients},
        logo=logo,
        color=color,
        include_patients_section=report_config.include_patients_section
    ))

    html_file_name = f'report_{get_formatted_now()}.html'
    html_file_full_path = os.path.join(TMP_DIR, html_file_name)

    with open(html_file_full_path, 'w', encoding='utf-8') as text_file:
        text_file.write(html)

    return TMP_DIR, html_file_name


# pylint: disable=too-many-arguments
def generate_pdf_report(
        txm_event: TxmEvent,
        configuration_db_id: int,
        pairing_result_model: PairingResultModel,
        matching_id: int,
        report_config: ReportConfiguration,
        keep_html_file: bool = False
) -> Tuple[str, str]:
    directory, html_file_name = generate_html_report(
        txm_event,
        configuration_db_id,
        pairing_result_model,
        matching_id,
        report_config
    )

    html_file_full_path = os.path.join(directory, html_file_name)
    pdf_file_name = f'report_{get_formatted_now()}.pdf'
    pdf_file_full_path = os.path.join(TMP_DIR, pdf_file_name)

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

    if not keep_html_file and os.path.exists(html_file_full_path):
        os.remove(html_file_full_path)

    return TMP_DIR, pdf_file_name


def export_patients_to_xlsx_file(patients_dto: Dict[str, Union[List[DonorDTOOut], List[Recipient]]]) -> BytesIO:
    @dataclass
    class PatientPair:
        # pylint: disable=too-many-instance-attributes
        donor_medical_id: str
        donor_internal_medical_id: str
        donor_country: str
        donor_height: int
        donor_weight: float
        donor_sex: str
        donor_year_of_birth: int
        donor_blood_group: str
        donor_note: str
        donor_type: str
        donor_antigens: str
        recipient_medical_id: str = ''
        recipient_internal_medical_id: str = ''
        recipient_country: str = ''
        recipient_height: int = None
        recipient_weight: float = None
        recipient_sex: str = ''
        recipient_year_of_birth: int = None
        recipient_note: str = ''
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
            donor_internal_medical_id=donor.internal_medical_id,
            donor_country=donor.parameters.country_code.value,
            donor_height=donor.parameters.height,
            donor_weight=donor.parameters.weight,
            donor_sex=donor.parameters.sex.value if donor.parameters.sex is not None else '',
            donor_year_of_birth=donor.parameters.year_of_birth,
            donor_note=donor.parameters.note,
            donor_blood_group=donor.parameters.blood_group,
            donor_type=donor_type_label_filter(donor.donor_type),
            donor_antigens=' '.join([hla.raw_code for hla in donor.parameters.hla_typing.hla_types_raw_list]),
        )
        if recipient is not None:
            antibodies: List[HLAAntibody] = []
            for antibodies_per_group in recipient.hla_antibodies.hla_antibodies_per_groups_over_cutoff:
                antibodies.extend(antibodies_per_group.hla_antibody_list)

            patient_pair = replace(
                patient_pair,
                recipient_medical_id=recipient.medical_id,
                recipient_internal_medical_id=recipient.internal_medical_id,
                recipient_country=recipient.parameters.country_code.value,
                recipient_height=recipient.parameters.height,
                recipient_weight=recipient.parameters.weight,
                recipient_sex=recipient.parameters.sex.value if recipient.parameters.sex is not None else '',
                recipient_year_of_birth=recipient.parameters.year_of_birth,
                recipient_note=recipient.parameters.note,
                recipient_blood_group=recipient.parameters.blood_group,
                recipient_acceptable_blood_groups=(
                    ', '.join(blood_group for blood_group in recipient.acceptable_blood_groups)
                ),
                recipient_antigens=' '.join(
                    [hla.code.display_code for hla_group in recipient.parameters.hla_typing.hla_per_groups
                     for hla in hla_group.hla_types]),
                recipient_antibodies=' '.join([antibody.raw_code for antibody in antibodies]),
            )
        patient_pairs.append(patient_pair)

    df_with_patients = pd.DataFrame(patient_pairs)

    # Save to xls file and set some formatting
    # pylint: disable=abstract-class-instantiated
    buffer = BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    df_with_patients.to_excel(writer, sheet_name='Patients', index=False)
    # pylint: disable=no-member
    workbook = writer.book
    worksheet = writer.sheets['Patients']
    # wrap text in the cells
    workbook_format = workbook.add_format({'text_wrap': True})
    # increase columns width to 20
    worksheet.set_column('A:S', 20, workbook_format)

    writer.close()
    buffer.seek(0)

    return buffer


def _copy_assets():
    if os.path.exists(TMP_DIR):
        old_dir = os.path.join(TEMPLATES_DIR, 'assets/')
        new_dir = TMP_DIR + '/assets/'
        copy_tree(old_dir, new_dir)


def _prepare_tmp_dir():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)


def _prune_old_reports():
    now = time.time()
    for filename in os.listdir(TMP_DIR):
        if os.path.getmtime(os.path.join(TMP_DIR, filename)) < now - 1 * 86400:  # 1 day
            if os.path.isfile(os.path.join(TMP_DIR, filename)):
                os.remove(os.path.join(TMP_DIR, filename))


def _get_theme() -> Tuple[str, str]:
    conf = get_application_configuration()
    return (LOGO_MILD_BLUE, COLOR_MILD_BLUE) if conf.colour_scheme == ApplicationColourScheme.STAGING \
        else (LOGO_IKEM, COLOR_IKEM)


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


def show_recipient_requirements_info_filter(requirements: Optional[RecipientRequirements]) -> bool:
    return requirements is not None and (
            requirements.require_compatible_blood_group or
            requirements.require_better_match_in_compatibility_index or
            requirements.require_better_match_in_compatibility_index_or_blood_group or
            requirements.max_donor_weight is not None or
            requirements.min_donor_weight is not None or
            requirements.max_donor_height is not None or
            requirements.min_donor_height is not None or
            requirements.max_donor_age is not None or
            requirements.min_donor_age is not None
    )


def recipient_requirements_info_filter(requirements: Optional[RecipientRequirements]) -> str:
    if requirements is None:
        return 'NO/NO/NO/-/-/-/-/-/-'

    return '/'.join([
        'YES' if requirements.require_compatible_blood_group else 'NO',
        'YES' if requirements.require_better_match_in_compatibility_index else 'NO',
        'YES' if requirements.require_better_match_in_compatibility_index_or_blood_group else 'NO',
        str(requirements.max_donor_weight) if requirements.max_donor_weight is not None else '-',
        str(requirements.min_donor_weight) if requirements.min_donor_weight is not None else '-',
        str(requirements.max_donor_height) if requirements.max_donor_height is not None else '-',
        str(requirements.min_donor_height) if requirements.min_donor_height is not None else '-',
        str(requirements.max_donor_age) if requirements.max_donor_age is not None else '-',
        str(requirements.min_donor_age) if requirements.min_donor_age is not None else '-',

    ])


def score_color_filter(score: Optional[float], max_score: Optional[float]):
    # wkhtmltopdf does not support linear-gradients css style that is used in fe and makes
    # exporting super-slow so we define percentage->color mapping in this function
    if max_score is None or max_score < 1:
        max_score = 1

    if score is None:
        percentage = 0
    elif score == -1:
        return '#ff0000'  # bad-matching
    else:
        percentage = 100 * score / max_score

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
    if hla.code.display_code == hla.raw_code:
        return f'{hla.code.display_code}'
    else:
        return f'{hla.code.display_code} ({hla.raw_code})'


jinja2.filters.FILTERS.update({
    'country_combination_filter': country_combination_filter,
    'donor_recipient_score_filter': donor_recipient_score_filter,
    'country_code_from_country_filter': country_code_from_country_filter,
    'patient_by_medical_id_filter': patient_by_medical_id_filter,
    'patient_height_and_weight_filter': patient_height_and_weight_filter,
    'show_recipient_requirements_info_filter': show_recipient_requirements_info_filter,
    'recipient_requirements_info_filter': recipient_requirements_info_filter,
    'score_color_filter': score_color_filter,
    'donor_type_label_filter': donor_type_label_filter,
    'donor_type_label_from_round_filter': donor_type_label_from_round_filter,
    'round_index_from_order_filter': round_index_from_order_filter,
    'hla_type_filter': hla_type_filter,
})
