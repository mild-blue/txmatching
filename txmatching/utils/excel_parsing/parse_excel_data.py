import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

import pandas as pd
from werkzeug.datastructures import FileStorage

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import COMPATIBLE_BLOOD_GROUPS, BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.excel_parsing.countries_for_excel import \
    country_code_from_id

DEFAULT_CUTOFF_FOR_EXCEL = 2000
DEFAULT_MFI = 4 * DEFAULT_CUTOFF_FOR_EXCEL

EXPLANATION_FILE_STILL_SAVED = 'If you believe the file is in correct format or you are unable to fix the issue ' \
                               'contact us on the contact email and we will figure out what to do. ' \
                               'The raw file was securely saved to our database'


class ExcelSource(str, Enum):
    IKEM = 'IKEM'
    BEL_2 = 'BEL_2'

# is needed here because kw_args in dataclass is not handled well by pylint
# pylint: disable=too-many-instance-attributes,unexpected-keyword-arg
@dataclass
class ExcelColumnsMap:
    donor_id: str
    donor_blood_group: str
    donor_typing: str
    recipient_blood_group: str
    recipient_acceptable_bloods: str
    recipient_typization: str
    recipient_id: str
    recipient_antibodies: str


# pylint: enable=too-many-instance-attributes

EXCEL_COLUMNS_MAPS = {
    ExcelSource.IKEM: ExcelColumnsMap(
        'DONOR',
        'BLOOD GROUP donor',
        'TYPIZATION DONOR',
        'BLOOD GROUP recipient',
        'Acceptable blood group',
        'TYPIZATION RECIPIENT',
        'RECIPIENT',
        'luminex  cut-off (2000 MFI) varianta 2',
    ),
    ExcelSource.BEL_2: ExcelColumnsMap(
        donor_id='Donor ID',
        donor_blood_group='ABO DONOR',
        donor_typing='HLA Typing DONOR',
        recipient_blood_group='ABO RECIPIENT',
        recipient_acceptable_bloods='Acceptable blood group',
        recipient_typization='HLA typing RECIPIENT',
        recipient_id='Recipient ID',
        recipient_antibodies='Unacceptable Antigens',
    ),
}

SKIP_ROWS_MAP = {
    ExcelSource.IKEM: 1,
    ExcelSource.BEL_2: 2
}

logger = logging.getLogger(__name__)


def _parse_blood_group(blood_group_str: Union[str, int]) -> BloodGroup:
    if isinstance(blood_group_str, float) and blood_group_str == 0.0:
        return BloodGroup.ZERO
    blood_group_str = str(blood_group_str).replace('+', '').replace('-', '').strip()
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
    if not isinstance(hla_codes_str, str):
        return []
    if 'neg' in str(hla_codes_str).lower():
        return []
    if '/' in str(hla_codes_str).lower():
        return []
    # remove codes in brackets, they are only in detail all the split codes for broade in front of the bracket
    hla_codes_str = re.sub(r'\(.*?\)', '', hla_codes_str)
    hla_codes_str = re.sub(r'\n', '', hla_codes_str)
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


def _get_donor_upload_dto_from_row(row: Dict[str, str],
                                   related_recipient_medical_id: Optional[str],
                                   column_map: ExcelColumnsMap) -> DonorUploadDTO:
    donor_id = row[column_map.donor_id]
    blood_group = _parse_blood_group(row[column_map.donor_blood_group])
    hla_typing = _parse_hla(row[column_map.donor_typing])

    if related_recipient_medical_id:
        donor_type = DonorType.DONOR
    else:
        # TODO this is not true, some are altruists, but this information is not available in the Excel at the moment
        donor_type = DonorType.BRIDGING_DONOR
    return DonorUploadDTO(medical_id=donor_id,
                          blood_group=blood_group,
                          donor_type=donor_type,
                          hla_typing=hla_typing,
                          related_recipient_medical_id=related_recipient_medical_id,
                          )


def _get_recipient_upload_dto_from_row(row: Dict[str, str],
                                       column_map: ExcelColumnsMap) -> Optional[RecipientUploadDTO]:
    recipient_id = row[column_map.recipient_id]
    if pd.isna(recipient_id):
        return None
    else:
        blood_group = _parse_blood_group(row[column_map.recipient_blood_group])
        hla_typing = _parse_hla(row[column_map.recipient_typization])
        antibodies_recipient = _parse_hla_antibodies(row[column_map.recipient_antibodies])
        acceptable_blood_groups_recipient = _parse_acceptable_blood_groups(
            row[column_map.recipient_acceptable_bloods],
            blood_group=blood_group)

        return RecipientUploadDTO(medical_id=recipient_id,
                                  hla_antibodies=antibodies_recipient,
                                  acceptable_blood_groups=acceptable_blood_groups_recipient,
                                  hla_typing=hla_typing,
                                  blood_group=blood_group
                                  )


def parse_excel_data(file_io: Union[str, FileStorage],
                     txm_event_name: str,
                     country: Optional[Country],
                     add_to_existing_patients: bool = True,
                     excel_source: ExcelSource = ExcelSource.IKEM) -> List[PatientUploadDTOIn]:
    logger.info('Parsing patient data from file')
    try:
        data = pd.read_excel(file_io, skiprows=SKIP_ROWS_MAP[excel_source])
    except Exception as error:
        raise InvalidArgumentException(
            f'Error during load of excel file:{error}. {EXPLANATION_FILE_STILL_SAVED}') from error
    column_map = EXCEL_COLUMNS_MAPS[excel_source]
    missing_columns = set(column_map.__dict__.values()).difference(set(data.columns))
    if len(missing_columns) > 0:
        raise InvalidArgumentException(f'Missing columns: {missing_columns}. {EXPLANATION_FILE_STILL_SAVED}')
    parsed_data = {}

    try:
        for _, row in data.iterrows():
            recipient_medical_id = row[column_map.recipient_id] if isinstance(row[column_map.recipient_id], str) else None
            donor = _get_donor_upload_dto_from_row(row, recipient_medical_id, column_map)
            if country:
                row_country = country
            else:
                row_country = country_code_from_id(donor.medical_id)

            if row_country in parsed_data:
                parsed_data[row_country].donors += [donor]
                if recipient_medical_id:
                    if recipient_medical_id not in [r.medical_id for r in parsed_data[row_country].recipients]:
                        parsed_data[row_country].recipients += [_get_recipient_upload_dto_from_row(row, column_map)]
            else:
                parsed_data[row_country] = PatientUploadDTOIn(
                    txm_event_name=txm_event_name,
                    country=row_country,
                    donors=[donor],
                    recipients=[_get_recipient_upload_dto_from_row(row, column_map)] if recipient_medical_id else [],
                    add_to_existing_patients=add_to_existing_patients
                )
    except Exception as error:
        raise InvalidArgumentException(f'Error during patient extraction from excel: {error} '
                                       f'{EXPLANATION_FILE_STILL_SAVED}') from error

    return list(parsed_data.values())
