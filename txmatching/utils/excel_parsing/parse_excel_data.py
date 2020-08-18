import logging
import math
import os
import re
from typing import Dict, List, Tuple, Union

import pandas as pd
from werkzeug.datastructures import FileStorage

from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorDTO
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientDTO
from txmatching.patients.patient_parameters import (HLAAntibodies,
                                                         HLAAntigens,
                                                         PatientParameters)
from txmatching.utils.blood_groups import COMPATIBLE_BLOOD_GROUPS
from txmatching.utils.countries import AUT, CZE, IL
from txmatching.utils.hla_system.hla_table import (HLA_A, HLA_A_BROAD,
                                                        HLA_B, HLA_B_BROAD,
                                                        HLA_BW, HLA_CW,
                                                        HLA_CW_BROAD, HLA_DQ,
                                                        HLA_DQ_BROAD, HLA_DR,
                                                        HLA_DR_BROAD, HLA_DRDR)

_valid_blood_groups = ['A', 'B', '0', 'AB']

_valid_allele_codes = HLA_A + HLA_B + HLA_BW + HLA_CW + HLA_DQ + HLA_DR + HLA_DRDR + \
                      HLA_A_BROAD + HLA_B_BROAD + HLA_CW_BROAD + HLA_DQ_BROAD + HLA_DR_BROAD

_unknown_allele_codes = set()

logger = logging.getLogger(__name__)


def _parse_blood_group(blood_group_str: Union[str, int]) -> str:
    blood_group_str = str(blood_group_str).strip()
    if blood_group_str not in _valid_blood_groups:
        raise ValueError(f'Encountered invalid group in blood group string {blood_group_str}')
    return blood_group_str


def _parse_acceptable_blood_groups(acceptable_blood_groups: Union[str, float, int], blood_group: str) -> List[str]:
    basic_acceptable_blood_groups = COMPATIBLE_BLOOD_GROUPS[blood_group]
    if not isinstance(acceptable_blood_groups, str) and math.isnan(acceptable_blood_groups):
        return list(basic_acceptable_blood_groups)
    blood_groups_str = str(acceptable_blood_groups).strip()
    acceptable_blood_groups = {_parse_blood_group(acceptable_blood_group) for acceptable_blood_group in
                               re.split('[, ]+', blood_groups_str)}

    return list(acceptable_blood_groups.union(basic_acceptable_blood_groups))


def _parse_hla(hla_allele_str: str) -> List[str]:
    if 'neg' in hla_allele_str.lower():
        return []

    allele_codes = re.split('[,. ()]+', hla_allele_str)
    allele_codes = [code for code in allele_codes if len(code) > 0]
    checked_allele_codes = [code for code in allele_codes if code in _valid_allele_codes]
    if len(checked_allele_codes) != len(allele_codes):
        unknown_allele_codes = []
        for code in allele_codes:
            if code not in checked_allele_codes:
                unknown_allele_codes.append(code)
                _unknown_allele_codes.add(code)
        logger.warning(f"Following codes are not in the antigen codes table: \n {', '.join(unknown_allele_codes)}")
        logger.warning(f'They were encountered in allele codes string {hla_allele_str}\n')

    return allele_codes


def _country_code_from_id(patient_id: str) -> str:
    if re.match('[PD][0-9]{4}', patient_id):
        return IL

    if re.match('[PD][0-9]{1,2}', patient_id):
        return CZE

    if patient_id.startswith('W-'):
        return AUT

    raise ValueError(f'Could not assign country code to {patient_id}')


def parse_excel_data(file_io: Union[str, FileStorage]) -> Tuple[List[DonorDTO], List[RecipientDTO]]:
    logger.info('Parsing patient data from file')
    data = pd.read_excel(file_io, skiprows=1)
    donors = list()
    recipients = list()
    for _, row in data.iterrows():
        donor = get_donor_from_row(row)
        donors.append(donor)
        recipient_id = row['RECIPIENT']
        if not pd.isna(recipient_id):
            recipient = get_recipient_from_row(row, recipient_id, donor)
            recipients.append(recipient)

    return donors, recipients


def get_donor_from_row(row: Dict) -> DonorDTO:
    donor_id = row['DONOR']
    blood_group_donor = _parse_blood_group(row['BLOOD GROUP donor'])
    typization_donor = _parse_hla(row['TYPIZATION DONOR'])
    country_code_donor = _country_code_from_id(donor_id)
    donor_params = PatientParameters(blood_group=blood_group_donor,
                                     hla_antigens=HLAAntigens(typization_donor),
                                     country_code=country_code_donor)
    return DonorDTO(medical_id=donor_id, parameters=donor_params)


def get_recipient_from_row(row: Dict, recipient_id: str, donor: DonorDTO) -> RecipientDTO:
    blood_group_recipient = _parse_blood_group(row['BLOOD GROUP recipient'])
    typization_recipient = _parse_hla(row['TYPIZATION RECIPIENT'])
    antibodies_recipient = _parse_hla(row['luminex  cut-off (2000 MFI) varianta 2'])
    acceptable_blood_groups_recipient = _parse_acceptable_blood_groups(row['Acceptable blood group'],
                                                                       blood_group_recipient)
    country_code_recipient = _country_code_from_id(recipient_id)

    recipient_params = PatientParameters(blood_group=blood_group_recipient,
                                         hla_antigens=HLAAntigens(typization_recipient),
                                         hla_antibodies=HLAAntibodies(antibodies_recipient),
                                         acceptable_blood_groups=acceptable_blood_groups_recipient,
                                         country_code=country_code_recipient)
    return RecipientDTO(medical_id=recipient_id, parameters=recipient_params,
                        related_donor=donor)


if __name__ == '__main__':
    patient_data_path = os.getenv('PATIENT_DATA_PATH')
    final_donors, final_recipients = parse_excel_data(patient_data_path)
    logger.info('\nDonors: \n' + '-' * 50 + '\n')
    for final_donor in final_donors:
        logger.info(final_donor)

    logger.info('\nRecipients: \n' + '-' * 50 + '\n')
    for final_recipient in final_recipients:
        logger.info(final_recipient)

    logger.info(f'\nUnknown allele codes: {sorted(_unknown_allele_codes)}')
