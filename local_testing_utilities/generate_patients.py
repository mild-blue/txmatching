import dataclasses
import json
import os
import random
import re
from enum import Enum
from typing import List, Optional, Tuple

import pandas as pd
from dacite import Config, from_dict

from local_testing_utilities.utils import create_or_overwrite_txm_event
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLA_GROUPS_PROPERTIES, HLAGroup, Sex
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.hla_system.hla_regexes import try_convert_high_res_with_letter
from txmatching.utils.hla_system.hla_table import HIGH_RES_TO_SPLIT_OR_BROAD, \
    PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS

BRIDGING_PROBABILITY = 0.8
TXM_EVENT_NAME = 'high_res_example_data'
DATA_FOLDER = get_absolute_path(f'tests/resources/{TXM_EVENT_NAME}/')


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


SAMPLE = set(range(1, 40))


def get_codes(hla_group: HLAGroup, sample=None):
    if sample is None:
        sample = SAMPLE
    all_high_res = [high_res for high_res, split_or_broad_or_nan in HIGH_RES_TO_SPLIT_OR_BROAD.items() if
                    split_or_broad_or_nan is not None and not pd.isna(split_or_broad_or_nan) and re.match(
                        HLA_GROUPS_PROPERTIES[hla_group].split_code_regex, split_or_broad_or_nan) and high_res.count(
                        ':') == 1]
    return [high_res for i, high_res in enumerate(all_high_res) if i in sample]


def get_codes_with_letter(hla_group: HLAGroup, sample=None):
    if sample is None:
        sample = set(range(1, 15))

    all_high_res_with_letter = [try_convert_high_res_with_letter(high_res) for high_res in
                                PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS.index.tolist()]

    all_high_res_with_letter_grouped = [code for code in all_high_res_with_letter if
                                        re.match(HLA_GROUPS_PROPERTIES[hla_group].high_res_code_regex, code)]

    def get_code_with_letter(letter: str):
        return [code for code in all_high_res_with_letter_grouped if code[-1] == letter]

    result = []
    for letter in ['N', 'Q', 'L', 'S']:
        codes = get_code_with_letter(letter)
        result += codes if len(codes) < 10 else random.sample(codes, 10)

    return random.sample(result, len(sample))


TypizationFor = {
    HLAGroup.A: get_codes(HLAGroup.A) + get_codes_with_letter(HLAGroup.A),
    HLAGroup.B: get_codes(HLAGroup.B) + get_codes_with_letter(HLAGroup.B),
    HLAGroup.DRB1: get_codes(HLAGroup.DRB1) + get_codes_with_letter(HLAGroup.DRB1),
    # HLAGroup.CW: get_codes(HLAGroup.CW),
    HLAGroup.DP: get_codes(HLAGroup.DP) + get_codes_with_letter(HLAGroup.DP),
    HLAGroup.DQ: get_codes(HLAGroup.DQ) + get_codes_with_letter(HLAGroup.DQ),
}


def get_random_hla_type(hla_group: HLAGroup):
    return random.choice(TypizationFor[hla_group])


def generate_hla_typing() -> List[str]:
    typization = []
    for hla_group in TypizationFor:
        typization.append(get_random_hla_type(hla_group))
        typization.append(get_random_hla_type(hla_group))

    return typization


CUTOFF = 2000


def generate_antibodies() -> List[HLAAntibodiesUploadDTO]:
    antibodies = []
    for hla_group in TypizationFor:
        for hla_code in TypizationFor[hla_group]:
            above_cutoff = random_true_with_prob(0.8)
            mfi = int(CUTOFF * 2) if above_cutoff else int(CUTOFF / 2)
            antibodies.append(HLAAntibodiesUploadDTO(
                cutoff=CUTOFF,
                mfi=mfi,
                name=hla_code
            ))
    return antibodies


def generate_patient(country: Country, i: int) -> Tuple[DonorUploadDTO, Optional[RecipientUploadDTO]]:
    is_bridging = random_true_with_prob(BRIDGING_PROBABILITY)
    blood_group_donor = random_blood_group()
    donor_type = DonorType.BRIDGING_DONOR if is_bridging else DonorType.DONOR
    recipient_id = f'{country}_{i}R' if not is_bridging else None
    donor = DonorUploadDTO(
        donor_type=donor_type,
        blood_group=blood_group_donor,
        related_recipient_medical_id=recipient_id,
        hla_typing=generate_hla_typing(),
        medical_id=f'{country}_{i}',
        height=generate_random_height(),
        weight=generate_random_weight(),
        year_of_birth=generate_random_yob(),
        sex=Sex.F,
        note=generate_random_note(),
        internal_medical_id='internal_medical_id'
    )
    if is_bridging:
        recipient = None
    else:
        blood_group_recipient = random_blood_group()
        recipient = RecipientUploadDTO(
            blood_group=blood_group_recipient,
            hla_typing=generate_hla_typing(),
            hla_antibodies=generate_antibodies(),
            acceptable_blood_groups=[],
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


def generate_patients_for_one_country(country: Country, txm_event_name: str, count: int) -> PatientUploadDTOIn:
    pairs = [generate_patient(country, i) for i in range(0, count)]
    recipients = [recipient for _, recipient in pairs if recipient]
    donors = [donor for donor, _ in pairs]

    return PatientUploadDTOIn(
        add_to_existing_patients=False,
        txm_event_name=txm_event_name,
        country=country,
        recipients=recipients,
        donors=donors,
    )


def generate_patients(txm_event_name: str = TXM_EVENT_NAME,
                      countries: Optional[List[Country]] = None,
                      count_per_country=10) -> List[PatientUploadDTOIn]:
    if countries is None:
        countries = [Country.CZE, Country.IND, Country.CAN]
    patient_upload_objects = []
    for country in countries:
        patient_upload_objects.append(
            generate_patients_for_one_country(country, txm_event_name=txm_event_name, count=count_per_country))
    return patient_upload_objects


def store_generated_patients_from_folder():
    patient_upload_objects = []
    for filename in os.listdir(DATA_FOLDER):
        with open(f'{DATA_FOLDER}{filename}') as file_to_load:
            patient_upload_dto = from_dict(data_class=PatientUploadDTOIn,
                                           data=json.load(file_to_load), config=Config(cast=[Enum]))
            patient_upload_objects.append(patient_upload_dto)
    store_generated_patients(patient_upload_objects)


def store_generated_patients(generated_patients: List[PatientUploadDTOIn]):
    create_or_overwrite_txm_event(TXM_EVENT_NAME)
    for patient_upload_dto in generated_patients:
        replace_or_add_patients_from_one_country(patient_upload_dto)


if __name__ == '__main__':
    for upload_object in generate_patients(TXM_EVENT_NAME):
        with open(f'{DATA_FOLDER}{TXM_EVENT_NAME}_{upload_object.country}.json', 'w') as f:
            json.dump(dataclasses.asdict(upload_object), f)
