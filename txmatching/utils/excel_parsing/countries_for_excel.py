import re

from txmatching.utils.enums import Country

TEST_PATIENT_ID_REGEX = re.compile(r'([0-9A-Z]{1,5})-([A-Z]{3})-([DR])')
PV28_PATIENT_ID_REGEX = re.compile(r'([A-Z]*)-[A-Z\d]*')
PV31_PATIENT_ID_REGEX = re.compile(r'CZ[RD]\d+')
PV28_COUNTRY_DICT = {
    'P': Country.CZE,
    'W': Country.AUT,
    'IS': Country.ISR,
    'G': Country.AUT,
    'I': Country.AUT
}
JULY_2020_COUNTRY_REGEX = re.compile(r'P|D|(W-)[A-Z\d]*')


def country_code_from_id(patient_id: str) -> Country:
    match = re.match(PV31_PATIENT_ID_REGEX, patient_id)
    if match:
        return Country.CZE

    match = re.match(TEST_PATIENT_ID_REGEX, patient_id)
    if match:
        return Country[match.group(2)]
    match = re.match(PV28_PATIENT_ID_REGEX, patient_id)
    if match:
        return PV28_COUNTRY_DICT[match.group(1)]
    match = re.match(JULY_2020_COUNTRY_REGEX, patient_id)
    if match:
        if re.match('[PD][0-9]{4}', patient_id):
            return Country.ISR

        elif re.match('[PD][0-9]{1,2}', patient_id):
            return Country.CZE

        elif patient_id.startswith('W-'):
            return Country.AUT

    raise ValueError(f'Could not assign country code to {patient_id}')
