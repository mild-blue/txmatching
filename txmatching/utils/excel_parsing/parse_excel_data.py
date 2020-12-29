import logging
import re
from typing import Dict, List, Union, Optional

import math
import pandas as pd
from werkzeug.datastructures import FileStorage

from txmatching.data_transfer_objects.patients.upload_dto.donor_upload_dto import DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.hla_antibodies_upload_dto import HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.patient_upload_dto_in import PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dto.recipient_upload_dto import RecipientUploadDTO
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup, COMPATIBLE_BLOOD_GROUPS
from txmatching.utils.enums import Country
from txmatching.utils.excel_parsing.countries_for_excel import \
    country_code_from_id

DEFAULT_CUTOFF_FOR_EXCEL = 2000
DEFAULT_MFI = 4 * DEFAULT_CUTOFF_FOR_EXCEL

logger = logging.getLogger(__name__)


def _parse_blood_group(blood_group_str: Union[str, int]) -> BloodGroup:
    if isinstance(blood_group_str, float) and blood_group_str == 0.0:
        return BloodGroup.ZERO
    blood_group_str = str(blood_group_str).strip()
    try:
        return BloodGroup(blood_group_str)
    except Exception as error:
        raise ValueError(f'Encountered invalid group in blood group string {blood_group_str}') from error


def _parse_acceptable_blood_groups(acceptable_blood_groups: Union[str, float, int],
                                   blood_group: str) -> List[BloodGroup]:
    basic_acceptable_blood_groups = COMPATIBLE_BLOOD_GROUPS[blood_group]
    if not isinstance(acceptable_blood_groups, str) and math.isnan(acceptable_blood_groups):
        return list(basic_acceptable_blood_groups)
    blood_groups_str = str(acceptable_blood_groups).strip()
    acceptable_blood_groups = {_parse_blood_group(acceptable_blood_group) for acceptable_blood_group in
                               re.split('[, ]+', blood_groups_str)}

    return list(acceptable_blood_groups.union(basic_acceptable_blood_groups))


def _parse_hla(hla_codes_str: str) -> List[str]:
    if 'neg' in hla_codes_str.lower():
        return []
    # remove codes in brackets, they are only in detail all the split codes for broade in front of the bracket
    hla_codes_str = re.sub(r'\(.*?\)', '', hla_codes_str)
    hla_codes = re.split('[,. ()]+', hla_codes_str)
    hla_codes = [code.upper() for code in hla_codes if len(code) > 0]

    return hla_codes


def _parse_hla_antibodies(hla_allele_str: str) -> List[HLAAntibodiesUploadDTO]:
    hla_codes = _parse_hla(hla_allele_str)
    # value and cut_off are just temporary values for now
    return [HLAAntibodiesUploadDTO(
        mfi=DEFAULT_MFI,
        cutoff=DEFAULT_CUTOFF_FOR_EXCEL,
        name=hla_code
    ) for hla_code in hla_codes]


def _get_donor_upload_dto_from_row(row: Dict,
                                   related_recipient: Optional[RecipientUploadDTO]) -> DonorUploadDTO:
    donor_id = row['DONOR']
    blood_group = _parse_blood_group(row['BLOOD GROUP donor'])
    hla_typing = _parse_hla(row['TYPIZATION DONOR'])

    if related_recipient:
        donor_type = DonorType.DONOR
    else:
        donor_type = DonorType.BRIDGING_DONOR
    return DonorUploadDTO(medical_id=donor_id,
                          blood_group=blood_group,
                          donor_type=donor_type,
                          hla_typing=hla_typing,
                          related_recipient_medical_id=related_recipient.medical_id if related_recipient else None,
                          )


def _get_recipient_upload_dto_from_row(row: Dict) -> Optional[RecipientUploadDTO]:
    recipient_id = row['RECIPIENT']
    if pd.isna(recipient_id):
        return None
    else:
        blood_group = _parse_blood_group(row['BLOOD GROUP recipient'])
        hla_typing = _parse_hla(row['TYPIZATION RECIPIENT'])
        antibodies_recipient = _parse_hla_antibodies(row['luminex  cut-off (2000 MFI) varianta 2'])
        acceptable_blood_groups_recipient = _parse_acceptable_blood_groups(row['Acceptable blood group'],
                                                                           blood_group=blood_group)

        return RecipientUploadDTO(medical_id=recipient_id,
                                  hla_antibodies=antibodies_recipient,
                                  acceptable_blood_groups=acceptable_blood_groups_recipient,
                                  hla_typing=hla_typing,
                                  blood_group=blood_group
                                  )


def parse_excel_data(file_io: Union[str, FileStorage],
                     txm_event_name: str,
                     country: Optional[Country]) -> List[PatientUploadDTOIn]:
    logger.info('Parsing patient data from file')
    data = pd.read_excel(file_io, skiprows=1)
    parsed_data = dict()

    for _, row in data.iterrows():
        recipient = _get_recipient_upload_dto_from_row(row)
        donor = _get_donor_upload_dto_from_row(row, recipient)
        if country:
            row_country = country
        else:
            row_country = country_code_from_id(donor.medical_id)
        if row_country in parsed_data:
            parsed_data[row_country].donors += [donor]
            if recipient:
                parsed_data[row_country].recipients += [recipient]
        else:
            parsed_data[row_country] = PatientUploadDTOIn(
                txm_event_name=txm_event_name,
                country=row_country,
                donors=[donor],
                recipients=[recipient] if recipient else []
            )

    return list(parsed_data.values())
