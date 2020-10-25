import logging
import math
import re
from typing import Dict, List, Tuple, Union

import pandas as pd
from werkzeug.datastructures import FileStorage

from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorExcelDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import (
    HLATypingDTO, PatientParametersDTO)
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientExcelDTO
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntibody,
                                                    HLAType)
from txmatching.utils.blood_groups import COMPATIBLE_BLOOD_GROUPS, BloodGroup
from txmatching.utils.excel_parsing.countries_for_excel import \
    country_code_from_id
from txmatching.utils.hla_system.hla_transformations_store import \
    parse_hla_raw_code_and_store_parsing_error_in_db

DEFAULT_CUTOFF_FOR_EXCEL = 2000
DEFAULT_MFI = 10000

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


def _parse_hla(hla_allele_str: str) -> List[HLAType]:
    if 'neg' in hla_allele_str.lower():
        return []

    allele_codes = re.split('[,. ()]+', hla_allele_str)
    allele_codes = [code.upper() for code in allele_codes if len(code) > 0]

    return [HLAType(
        raw_code=raw_code,
        code=parse_hla_raw_code_and_store_parsing_error_in_db(raw_code)
    ) for raw_code in allele_codes]


def _parse_hla_antibodies(hla_allele_str: str) -> HLAAntibodies:
    allele_codes = _parse_hla(hla_allele_str)
    # value and cut_off are just temporary values for now
    return HLAAntibodies(
        [HLAAntibody(
            mfi=DEFAULT_MFI,
            cutoff=DEFAULT_CUTOFF_FOR_EXCEL,
            raw_code=allele_code.raw_code,
            code=parse_hla_raw_code_and_store_parsing_error_in_db(allele_code.raw_code)
        ) for allele_code in allele_codes])


def parse_excel_data(file_io: Union[str, FileStorage]) -> Tuple[List[DonorExcelDTO], List[RecipientExcelDTO]]:
    logger.info('Parsing patient data from file')
    data = pd.read_excel(file_io, skiprows=1)
    donors = list()
    recipients = list()
    for _, row in data.iterrows():
        donor = get_donor_from_row(row)
        donors.append(donor)
        recipient_id = row['RECIPIENT']
        if not pd.isna(recipient_id):
            recipient = _get_recipient_from_row(row, recipient_id)
            recipients.append(recipient)
        else:
            recipients.append(None)

    return donors, recipients


def get_donor_from_row(row: Dict) -> DonorExcelDTO:
    donor_id = row['DONOR']
    blood_group_donor = _parse_blood_group(row['BLOOD GROUP donor'])
    typization_donor = _parse_hla(row['TYPIZATION DONOR'])
    country_code_donor = country_code_from_id(donor_id)
    donor_params = PatientParametersDTO(blood_group=blood_group_donor,
                                        hla_typing=HLATypingDTO(typization_donor),
                                        country_code=country_code_donor)
    return DonorExcelDTO(medical_id=donor_id, parameters=donor_params)


def _get_recipient_from_row(row: Dict, recipient_id: str) -> RecipientExcelDTO:
    blood_group_recipient = _parse_blood_group(row['BLOOD GROUP recipient'])
    typization_recipient = _parse_hla(row['TYPIZATION RECIPIENT'])
    antibodies_recipient = _parse_hla_antibodies(row['luminex  cut-off (2000 MFI) varianta 2'])
    acceptable_blood_groups_recipient = _parse_acceptable_blood_groups(row['Acceptable blood group'],
                                                                       blood_group_recipient)
    country_code_recipient = country_code_from_id(recipient_id)

    recipient_params = PatientParametersDTO(blood_group=blood_group_recipient,
                                            hla_typing=HLATypingDTO(typization_recipient),
                                            country_code=country_code_recipient)
    return RecipientExcelDTO(medical_id=recipient_id, parameters=recipient_params,
                             hla_antibodies=antibodies_recipient,
                             acceptable_blood_groups=acceptable_blood_groups_recipient,
                             recipient_cutoff=DEFAULT_CUTOFF_FOR_EXCEL)
