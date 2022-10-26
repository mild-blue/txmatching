import dataclasses
import json
import pandas as pd
import re
from datetime import date
from typing import List

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.get_absolute_path import get_absolute_path

HLA_DATA = get_absolute_path(f'local_testing_utilities/notebooks/italian_data/hla.csv')
PAIRS = get_absolute_path(f'local_testing_utilities/notebooks/italian_data/pairs.csv')

DEFAULT_MFI = 2000
DEFAULT_CUTOFF = 1500

ITALIAN_DATA_FOLDER = get_absolute_path('tests/resources/italian_data/')
TXM_EVENT_NAME = "ITALIAN_DATA"


# acceptable_blood_groups = {'0': [BloodGroup.ZERO],
#                            'A': [BloodGroup.A, BloodGroup.ZERO],
#                            'B': [BloodGroup.B, BloodGroup.ZERO],
#                            'AB': [BloodGroup.A, BloodGroup.AB, BloodGroup.B, BloodGroup.ZERO]}

def store_italian_data_in_json():
    parsed_patients = parse_italian_data()
    with open(f'{ITALIAN_DATA_FOLDER}{TXM_EVENT_NAME}_{parsed_patients.country}.json', 'w',
              encoding='utf-8') as f:
        json.dump(dataclasses.asdict(parsed_patients), f)


def parse_italian_data() -> PatientUploadDTOIn:
    df = pd.read_csv(HLA_DATA)

    donor_antigens_str = {}
    recipient_antigens_str = {}
    recipient_antibodies_str = {}

    for _, row in df.iterrows():
        if pd.isnull(row[1]):
            donor_antigens_str[row[0]] = ''
        else:
            donor_antigens_str[row[0]] = row[1]
        if pd.isnull(row[2]):
            recipient_antigens_str[row[0]] = ''
        else:
            recipient_antigens_str[row[0]] = row[2]
        if pd.isnull(row[3]):
            recipient_antibodies_str[row[0]] = ''
        else:
            recipient_antibodies_str[row[0]] = row[3]

    df = pd.read_csv(PAIRS)

    # 0       1        2                3         4            5                    6             7
    # Pair ID,Donor ID,Donor blood type,Donor age,Recipient ID,Recipient blood type,Recipient age,Acceptable blood type

    donors = []
    recipients = []

    for _, row in df.iterrows():
        donor_blood_group = row[2] if not pd.isnull(row[2]) else '0'
        recipient_blood_group = row[5] if not pd.isnull(row[5]) else 'AB'
        acceptable_blood_groups_split = row[7].split('|')
        acceptable_blood_groups = [BloodGroup(blood_group) for blood_group in acceptable_blood_groups_split]

        donors.append(
            DonorUploadDTO(
                medical_id=str(row[0]) + "_DONOR",
                blood_group=BloodGroup(donor_blood_group),
                hla_typing=_parse_hla(donor_antigens_str[row[0]]),
                donor_type=DonorType.DONOR,  # todo
                # TODO: toto treba prerobit, skaredo zatial poriesene
                year_of_birth=date.today().year - int(row[3]),
                related_recipient_medical_id=str(row[0]) + "_RECIPIENT"  # todo
            )
        )
        recipients.append(
            RecipientUploadDTO(
                acceptable_blood_groups=acceptable_blood_groups,
                medical_id=str(row[0]) + "_RECIPIENT",
                blood_group=BloodGroup(recipient_blood_group),
                hla_typing=_parse_hla(recipient_antigens_str[row[0]]),
                # TODO: toto treba prerobit, skaredo zatial poriesene
                year_of_birth=date.today().year - int(row[6]),
                hla_antibodies=_parse_hla_antibodies(recipient_antibodies_str[row[0]])
            )
        )

    return PatientUploadDTOIn(
        country=Country.ITA,
        txm_event_name=TXM_EVENT_NAME,
        donors=donors,
        recipients=recipients,
        add_to_existing_patients=False
    )


def _parse_hla(hla_codes_str: str) -> List[str]:
    if not isinstance(hla_codes_str, str):
        return []

    hla_codes_str = re.sub(r'\(.*?\)', '', hla_codes_str)
    hla_codes_str = re.sub(r'\n', '', hla_codes_str)

    hla_codes = hla_codes_str.split('|')
    hla_codes = [code.upper() for code in hla_codes if len(code) > 0]

    hla_codes_to_return = []
    for code in hla_codes:
        numeric_index = 0
        for index in range(len(code)):
            if code[index].isnumeric() is True:
                numeric_index = index
                break
        hla_type = code[0:numeric_index]
        if hla_type == "CW":
            hla_type = "C"
        if code.endswith("00"):
            code_to_return = hla_type + str(int(code[numeric_index:numeric_index+2]))
        else:
            if hla_type == "DP" or hla_type == "DQ" or hla_type == "DR":
                code_to_return = hla_type + "B1*" + code[numeric_index:numeric_index+2] + ":" + code[numeric_index+2:]
            else:
                code_to_return = hla_type + "*" + code[numeric_index:numeric_index+2] + ":" + code[numeric_index+2:]

        hla_codes_to_return.append(code_to_return)
    return hla_codes_to_return


def _parse_hla_antibodies(hla_allele_str: str) -> List[HLAAntibodiesUploadDTO]:
    hla_codes = _parse_hla(hla_allele_str)

    return [HLAAntibodiesUploadDTO(
        mfi=DEFAULT_MFI,
        cutoff=DEFAULT_CUTOFF,
        name=hla_code
    ) for hla_code in hla_codes]


if __name__ == '__main__':
    store_italian_data_in_json()
