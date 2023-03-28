import dataclasses
import itertools
import json
import os
import random
import re
from enum import Enum
from typing import List, Optional, Tuple

import pandas as pd
from dacite import Config, from_dict

from local_testing_utilities.utils import create_or_overwrite_txm_event
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.parsing_issue_service import \
    confirm_all_parsing_issues
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLA_GROUPS_PROPERTIES, HLAGroup, Sex
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_regexes import \
    HIGH_RES_REGEX_ENDING_WITH_LETTER
from txmatching.utils.hla_system.hla_table import (
    ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE,
    HIGH_RES_TO_SPLIT_OR_BROAD,
    PARSED_DATAFRAME_WITH_ULTRA_HIGH_RES_TRANSFORMATIONS, SPLIT_TO_BROAD,
    high_res_low_res_to_split_or_broad)

BRIDGING_PROBABILITY = 0.8
NON_DIRECTED_PROBABILITY = 0.9
GENERATED_TXM_EVENT_NAME = 'high_res_example_data'
CROSSMATCH_TXM_EVENT_NAME = 'mixed_resolution_with_crossmatch_types'
LARGE_DATA_FOLDER = get_absolute_path(f'tests/resources/{GENERATED_TXM_EVENT_NAME}/')
SMALL_DATA_FOLDER = get_absolute_path('tests/resources/high_res_example_small_data/')
SMALL_DATA_FOLDER_MULTIPLE_DONORS = get_absolute_path('tests/resources/high_res_example_small_data_multiple_donors/')
SMALL_DATA_FOLDER_MULTIPLE_DONORS_V2 = \
    get_absolute_path('tests/resources/high_res_example_small_data_multiple_donors_v2/')
SMALL_DATA_FOLDER_WITH_ROUND = get_absolute_path('tests/resources/high_res_example_small_data_with_round/')
SMALL_DATA_FOLDER_THEORETICAL = get_absolute_path('tests/resources/theoretical_ab_small_data/')
SMALL_DATA_FOLDER_WITH_NO_SOLUTION = get_absolute_path('tests/resources/high_res_example_small_data_with_no_solution/')
SMALL_DATA_FOLDER_WITH_CROSSMATCH = get_absolute_path(f'tests/resources/{CROSSMATCH_TXM_EVENT_NAME}/')


# is needed here because kw_args in dataclass is not handled very well by pylint
# pylint: disable=unexpected-keyword-arg
def generate_waiting_since() -> str:
    return f'{random.choice(range(2018, 2020))}-{random.choice(range(1, 12))}-{random.choice(range(1, 28))}'


def generate_random_transplants() -> int:
    return random.choice(range(0, 4))


def generate_random_sex() -> Sex:
    return random.choice(list(Sex))


def generate_random_height() -> int:
    return random.choice(range(150, 190))


def generate_random_weight() -> int:
    return random.choice(range(50, 110))


def generate_random_yob() -> int:
    return random.choice(range(1950, 2000))


def generate_random_note() -> str:
    return random.choice(
        ['Patient note foo', 'Patient note bar', 'Patient\nnote\nmultiline', '']
    )


def random_true_with_prob(prob: float):
    return random.uniform(0, 1) > prob


def random_blood_group() -> BloodGroup:
    rand = random.uniform(0, 1)
    if rand < 0.15:
        return BloodGroup.ZERO
    if rand < 0.5:
        return BloodGroup.A
    if rand < 0.9:
        return BloodGroup.B
    else:
        return BloodGroup.AB


def random_acceptable() -> List[BloodGroup]:
    rand = random.uniform(0, 1)
    if rand > 0.3:
        return []
    num_of_acceptable = random.randint(1, 4)
    blood_groups = {BloodGroup.ZERO, BloodGroup.A, BloodGroup.B, BloodGroup.AB}
    acceptable = random.sample(blood_groups, num_of_acceptable)
    return acceptable


SAMPLE_LENGTH = 40
SAMPLE = set(range(1, SAMPLE_LENGTH + 1))


def get_donor_type() -> DonorType:
    is_bridging = random_true_with_prob(BRIDGING_PROBABILITY)
    is_non_directed = random_true_with_prob(NON_DIRECTED_PROBABILITY)
    if is_non_directed:
        return DonorType.NON_DIRECTED
    elif is_bridging:
        return DonorType.BRIDGING_DONOR
    return DonorType.DONOR


def get_codes(hla_group: HLAGroup, used_as_antibody=False):
    if not used_as_antibody or hla_group not in [HLAGroup.DQ, HLAGroup.DP]:
        all_high_res = [high_res for high_res, split_or_broad_or_nan in HIGH_RES_TO_SPLIT_OR_BROAD.items() if
                        split_or_broad_or_nan is not None and not pd.isna(split_or_broad_or_nan) and re.match(
                            HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, split_or_broad_or_nan)
                        and high_res.count(':') == 1
                        and high_res not in ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE]
        return all_high_res[:SAMPLE_LENGTH]
    else:
        if hla_group == HLAGroup.DP:
            regex_alpha = r'(^DPA\d+)'
            regex_beta = r'(^DP\d+)'
            start = 'DP'
        else:
            regex_alpha = r'(^DQA\d+)'
            regex_beta = r'(^DQ\d+)'
            start = 'DQ'

        all_high_alpha = [high_res.split('*')[1] for high_res, split_or_broad_or_nan in
                          HIGH_RES_TO_SPLIT_OR_BROAD.items() if
                          split_or_broad_or_nan is not None and not pd.isna(split_or_broad_or_nan) and re.match(
                              regex_alpha, split_or_broad_or_nan)
                          and high_res.count(':') == 1
                          and high_res not in ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE
                          and len(high_res.split('*')[1]) == 5][:SAMPLE_LENGTH]
        all_high_beta = [high_res.split('*')[1] for high_res, split_or_broad_or_nan in
                         HIGH_RES_TO_SPLIT_OR_BROAD.items() if
                         split_or_broad_or_nan is not None and not pd.isna(split_or_broad_or_nan) and re.match(
                             regex_beta, split_or_broad_or_nan)
                         and high_res.count(':') == 1
                         and high_res not in ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE
                         and len(high_res.split('*')[1]) == 5][:SAMPLE_LENGTH]
        chain_mix = list(itertools.product(all_high_alpha, all_high_beta))

        def _rand_sample():
            sample = random.choice(chain_mix)
            chain_mix.remove(sample)
            return sample

        final_sample_mix = []
        for _ in range(SAMPLE_LENGTH):
            final_sample_mix.append(_rand_sample())

        return [f'{start}[{code_1},{code_2}]' for code_1, code_2 in final_sample_mix]


def try_convert_high_res_with_letter(high_res_or_ultra_high_res: str) -> Optional[str]:
    match = HIGH_RES_REGEX_ENDING_WITH_LETTER.search(high_res_or_ultra_high_res)
    if match:
        high_res = match.group()
        return high_res
    else:
        return ''


def get_sample_of_codes_with_letter(hla_group: HLAGroup):
    all_high_res_with_letter = [try_convert_high_res_with_letter(high_res) for high_res in
                                PARSED_DATAFRAME_WITH_ULTRA_HIGH_RES_TRANSFORMATIONS.index.tolist()]

    all_high_res_with_letter_grouped = [code for code in all_high_res_with_letter if
                                        re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, code)]

    def get_code_with_letter(letter: str):
        return [code for code in all_high_res_with_letter_grouped if code[-1] == letter]

    selected_codes_with_letter = []
    for letter in ['N', 'Q', 'L', 'S']:
        codes_for_one_letter = get_code_with_letter(letter)
        selected_codes_with_letter += codes_for_one_letter if len(codes_for_one_letter) < 10 else \
            random.sample(codes_for_one_letter, 10)

    return selected_codes_with_letter


TypizationSample = {
    HLAGroup.A: get_codes(HLAGroup.A),
    HLAGroup.B: get_codes(HLAGroup.B),
    HLAGroup.DRB1: get_codes(HLAGroup.DRB1),
    HLAGroup.DP: get_codes(HLAGroup.DP),
    HLAGroup.DQ: get_codes(HLAGroup.DQ),
}

AntibodySample = {
    HLAGroup.A: get_codes(HLAGroup.A, used_as_antibody=True),
    HLAGroup.B: get_codes(HLAGroup.B, used_as_antibody=True),
    HLAGroup.DRB1: get_codes(HLAGroup.DRB1, used_as_antibody=True),
    HLAGroup.DP: get_codes(HLAGroup.DP, used_as_antibody=True),
    HLAGroup.DQ: get_codes(HLAGroup.DQ, used_as_antibody=True),
}


def get_random_hla_type(hla_group: HLAGroup, has_letter_at_the_end: bool = False, high_res: bool = True):
    if has_letter_at_the_end:
        return random.choice(get_sample_of_codes_with_letter(hla_group))
    else:
        if high_res:
            return random.choice(TypizationSample[hla_group])
        else:
            code = high_res_low_res_to_split_or_broad(random.choice(TypizationSample[hla_group]))
            broad = random.choice([True, False])
            if broad:
                if code in SPLIT_TO_BROAD:
                    code = SPLIT_TO_BROAD.get(code)

            return code


def generate_hla_typing(has_letter_at_the_end: bool, high_res: bool = True) -> List[str]:
    typization = []
    hla_with_letter = random.choice(list(TypizationSample.keys())) if has_letter_at_the_end else None

    for hla_group in TypizationSample:
        undecidable = random.choices([True, False], weights=[0.15, 0.85], k=1)[0]
        if not undecidable:
            typization.append(get_random_hla_type(hla_group, has_letter_at_the_end=(hla_with_letter == hla_group),
                                                high_res=high_res))  # [0]
            rand = random.uniform(0, 1)
            if rand > 0.3:
                typization.append(get_random_hla_type(hla_group, high_res=high_res))  # [0]

    return typization


CUTOFF = 2000


def generate_antibodies() -> List[HLAAntibodiesUploadDTO]:
    antibodies = []
    for hla_codes_in_group in AntibodySample.values():
        for hla_code in hla_codes_in_group:
            above_cutoff = random_true_with_prob(0.8)
            mfi = int(CUTOFF * 2) if above_cutoff else int(CUTOFF / 2)
            antibodies.append(HLAAntibodiesUploadDTO(
                cutoff=CUTOFF,
                mfi=mfi,
                name=hla_code
            ))
    return antibodies


def generate_patient(country: Country, i: int, has_hla_with_letter_at_the_end: bool, high_res: bool = True) -> \
        Tuple[DonorUploadDTO, Optional[RecipientUploadDTO]]:
    blood_group_donor = random_blood_group()
    donor_type = get_donor_type()
    recipient_id = f'{country}_{i}R' if donor_type == DonorType.DONOR else None

    donor = DonorUploadDTO(
        donor_type=donor_type,
        blood_group=blood_group_donor,
        related_recipient_medical_id=recipient_id,
        hla_typing=generate_hla_typing(has_hla_with_letter_at_the_end, high_res),
        medical_id=f'{country}_{i}',
        height=generate_random_height(),
        weight=generate_random_weight(),
        year_of_birth=generate_random_yob(),
        sex=Sex.F,
        note=generate_random_note(),
        internal_medical_id='internal_medical_id'
    )
    if recipient_id is None:
        recipient = None
    else:
        blood_group_recipient = random_blood_group()
        recipient = RecipientUploadDTO(
            blood_group=blood_group_recipient,
            hla_typing=generate_hla_typing(has_hla_with_letter_at_the_end, high_res),
            hla_antibodies=generate_antibodies(),
            acceptable_blood_groups=random_acceptable(),
            medical_id=recipient_id,
            height=generate_random_height(),
            weight=generate_random_weight(),
            year_of_birth=generate_random_yob(),
            sex=generate_random_sex(),
            note=generate_random_note(),
            waiting_since=generate_waiting_since(),
            previous_transplants=generate_random_transplants(),
            internal_medical_id='internal_medical_id'
        )

    return donor, recipient


def generate_patients_for_one_country(country: Country, txm_event_name: str, count: int, high_res: bool,
                                      has_hla_letter_at_the_end: bool = False) -> PatientUploadDTOIn:
    count_hla_with_letter_at_the_end = 2
    pairs = [generate_patient(country, i, has_hla_letter_at_the_end, high_res) for i in
             range(0, count - count_hla_with_letter_at_the_end)] + \
            [generate_patient(country, i, has_hla_letter_at_the_end, high_res) for i in
             range(count - count_hla_with_letter_at_the_end, count)]
    recipients = [recipient for _, recipient in pairs if recipient]
    donors = [donor for donor, _ in pairs]

    return PatientUploadDTOIn(
        add_to_existing_patients=False,
        txm_event_name=txm_event_name,
        country=country,
        recipients=recipients,
        donors=donors,
    )


def generate_patients(txm_event_name: str = GENERATED_TXM_EVENT_NAME,
                      countries: Optional[List[Country]] = None,
                      count_per_country=10,
                      high_res: bool = True
                      ) -> List[PatientUploadDTOIn]:
    if countries is None:
        countries = [Country.CZE, Country.IND, Country.CAN]

    patient_upload_objects = []
    for country in countries:
        patient_upload_objects.append(
            generate_patients_for_one_country(
                country,
                txm_event_name=txm_event_name,
                count=count_per_country,
                high_res=high_res))
    return patient_upload_objects


def store_generated_patients_from_folder(folder=LARGE_DATA_FOLDER, txm_event_name=GENERATED_TXM_EVENT_NAME):
    patient_upload_objects = []
    for filename in os.listdir(folder):
        with open(f'{folder}{filename}', encoding='utf-8') as file_to_load:
            patient_upload_dto = from_dict(data_class=PatientUploadDTOIn,
                                           data=json.load(file_to_load), config=Config(cast=[Enum]))
            patient_upload_objects.append(patient_upload_dto)
    store_generated_patients(patient_upload_objects, txm_event_name)
    admin_id = AppUserModel.query.filter(AppUserModel.role == UserRole.ADMIN).first().id
    confirm_all_parsing_issues(admin_id)


def store_generated_patients(generated_patients: List[PatientUploadDTOIn],
                             txm_event_name=GENERATED_TXM_EVENT_NAME):
    txm_event = create_or_overwrite_txm_event(txm_event_name)
    for patient_upload_dto in generated_patients:
        replace_or_add_patients_from_one_country(patient_upload_dto)
    return txm_event


if __name__ == '__main__':
    RESOLUTION_MIX = True
    PATIENT_COUNT = 15
    DATA_FOLDER_TO_STORE_DATA = LARGE_DATA_FOLDER
    TXM_EVENT_NAME = 'high_res_example_data'

    if RESOLUTION_MIX:
        for upload_object in generate_patients(TXM_EVENT_NAME, [Country.CAN], PATIENT_COUNT, False):
            with open(f'{DATA_FOLDER_TO_STORE_DATA}{TXM_EVENT_NAME}_{upload_object.country}.json', 'w',
                      encoding='utf-8') as f:
                json.dump(dataclasses.asdict(upload_object), f)

        for upload_object in generate_patients(TXM_EVENT_NAME, [Country.CZE, Country.IND], PATIENT_COUNT, True):
            with open(f'{DATA_FOLDER_TO_STORE_DATA}{TXM_EVENT_NAME}_{upload_object.country}.json', 'w',
                      encoding='utf-8') as f:
                json.dump(dataclasses.asdict(upload_object), f)
    else:
        for upload_object in generate_patients(TXM_EVENT_NAME, [Country.CZE], PATIENT_COUNT):
            with open(f'{DATA_FOLDER_TO_STORE_DATA}{TXM_EVENT_NAME}_{upload_object.country}.json', 'w',
                      encoding='utf-8') as f:
                json.dump(dataclasses.asdict(upload_object), f)
