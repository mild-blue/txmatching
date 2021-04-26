import os
from dataclasses import asdict, dataclass
from typing import Optional, Tuple

import pandas as pd

from local_testing_utilities.notebook_utils.utils import parse_hla


@dataclass
class PatientPair:
    txm_event: str

    donor_name: str
    donor_blood_group: str
    donor_year_of_birth: int
    donor_relationship: str
    donor_typization: str

    recipient_name: str = ''
    recipient_blood_group: str = ''
    recipient_year_of_birth: str = ''
    recipient_typization: str = ''

    recipient_luminex_date: str = None
    recipient_luminex_1: str = None
    recipient_luminex_2: str = ''
    recipient_acceptable_blood: str = None


@dataclass
class ExcelColumnsMap:
    donor_name: str
    donor_blood_group: str
    donor_year_of_birth: int
    donor_relationship: str
    donor_typization: str

    recipient_name: str
    recipient_blood_group: str
    recipient_year_of_birth: str
    recipient_typization: str

    recipient_luminex_date: str
    recipient_luminex_1: str
    recipient_luminex_2: str
    recipient_acceptable_blood: str


COLUMNS_MAP = ExcelColumnsMap(
    ['Donor', 'DÁRCE'],
    ['BLOOD GROUP donor', 'KS', 'KS dárce', 'KS DÁRCE', 'Blood group', 'KS DÁRCE donor', 'KS  donor'],
    ['ID/age', 'ID', 'RČ'],
    ['RELATIONSHIP', 'VZTAH'],
    ['TYPIZATION DONOR', 'TYPIZACE', 'Typizace dárce', 'Typing', 'TYPIZACE DÁRCE'],

    [' RECIPIENT', 'RECIPIENT', 'PŘÍJEMCE'],
    ['BLOOD GROUP recipient', 'KS.1', 'KS příjemce', 'KS PŘÍJEMCE', 'Blood group.1'],
    ['ID/age.1', 'ID.1', 'RČ.1'],
    ['TYPIZATION RECIPIENT', 'TYPIZACE.1', 'Typizace příjemce', 'Typing.1', 'TYPIZACE PŘÍJEMCE'],

    ['datum luminex'],
    ['luminex varianta 1', 'Luminex varianta 1', 'LUMINEX: SA1>1000MFI,SA2>2000MFI', 'Luminex'],
    ['luminex  cut-off (2000 MFI) varianta 2', 'LUMINEX:SA1 a SA2>2000MFI', 'Luminex varianta 2', 'luminex posun cut-off', 'luminex posun cut off', 'luminex posun cut-off varianta 2'],
    ['Acceptable blood group', 'Povolené KS', 'allowed blood group', 'povolené KS.'],
)

PARSING_CONFIGS = [
    # txm_event, header, sheet_name, nrows, col_map, filename
    (10, 1, 0, None, COLUMNS_MAP, 'PV10_prehled.xlsx'),
    (11, 1, 0, None, COLUMNS_MAP, 'PV11_prehled_vysetreni.xlsx'),
    (12, 1, 0, None, COLUMNS_MAP, 'PV12finalni prehled.xlsx'),
    (13, 1, 2, None, COLUMNS_MAP, 'PV13finalni prehled vysetreni.xlsx'),
    (14, 0, 0, 5, COLUMNS_MAP, 'PV14_Czech_Vienna_final_results.xlsx'),
    (15, 1, 0, None, COLUMNS_MAP, 'PV15.xlsx'),
    (16, 1, 0, None, COLUMNS_MAP, 'PV16.xlsx'),
    (17, 1, 0, None, COLUMNS_MAP, 'PV17.xlsx'),
    (18, 2, 0, None, COLUMNS_MAP, 'PV18.xlsx'),
    (19, 0, 0, 8, COLUMNS_MAP, 'PV19.xlsx'),
    (20, 0, 0, 9, COLUMNS_MAP, 'PV20 + Vienna.xlsx'),
    (21, 0, 0, 11, COLUMNS_MAP, 'PV21.xlsx'),
    (22, 0, 0, None, COLUMNS_MAP, 'PV22.xlsx'),
    (23, 0, 0, 13, COLUMNS_MAP, 'PV23.xlsx'),
    (24, 0, 0, 12, COLUMNS_MAP, 'PV24.xlsx'),
    (25, 0, 0, 17, COLUMNS_MAP, 'PV25.xlsx'),
    # (26, 1, 'PV26 + Izrael.xlsx'),
    (26, 1, 0, 15, COLUMNS_MAP, 'PV26.xlsx'),
    (27, 1, 0, 11, COLUMNS_MAP, 'PV27.xlsx'),
    # (29, 1, 'PV28 + Izrael.xlsx'),
    (28, 1, 0, 15, COLUMNS_MAP, 'PV28 + Rakousko.xlsx'),
    (29, 1, 0, 13, COLUMNS_MAP, 'PV29.xlsx'),
    (30, 1, 0, 13, COLUMNS_MAP, 'PV30.xlsx'),
    (31, 1, 0, 10, COLUMNS_MAP, 'PV31_anon.xlsx'),
    # (33, 1, 'Přehled vyšetření k 14.1.2015.xlsx'),
    # (34, 1, 'Souhrn vysetreni k 23.5.2013.xls'),
    # (35, 1, 'Stav vyšetření k 10.6.2014.xlsx'),
    # (36, 1, 'Stav vyšetření k 13.02.2014.xls'),
    # (37, 1, 'Stav vyšetření k 20.11.2013.xls'),
    # (38, 1, 'Stav vyšetření k 4.9.2013.xls'),
    # (39, 1, 'Stav vyšetření k 4.9.2014.xlsx')
]


def _row_to_patient_pair(row: pd.Series, config: Tuple) -> Optional[PatientPair]:
    txm_event, header, sheet_name, nrows, col_map, filename = config

    col_map_dict = dict()
    for key, col_names in asdict(col_map).items():
        col_map_dict[key] = None
        for col_name in col_names:
            col_name = col_name.lower()
            if col_name in set(row.keys()):
                val = str(row[col_name]).strip().replace('    ', ' ')
                col_map_dict[key] = val if val not in ['nan', 'NAN', 'Null', 'X'] else ''
                continue

    missing_columns = {k: asdict(col_map)[k] for k, v in col_map_dict.items()
                       if v is None and k in {  # required columns
                           'donor_blood_group', 'donor_typization', 'recipient_blood_group', 'recipient_typization', 'recipient_luminex_2', 'recipient_acceptable_blood'
                       }}
    if len(missing_columns) > 0:
        print(f'Missing columns in {filename}: {missing_columns}.\n -- {set(row.keys())}')
        # raise ValueError(f'Missing columns: {missing_columns}. {filename}: {set(row.keys())}')

    if pd.isnull(col_map_dict['donor_typization']) or pd.isnull(col_map_dict['recipient_typization']):
        # This happens for and bridging or if row is empty. Uncomment to check it
        # print(f"Warning: Row ignored ({filename}): {row}")
        return None

    col_map_dict['donor_typization'] = parse_hla(col_map_dict['donor_typization'])
    col_map_dict['recipient_typization'] = parse_hla(col_map_dict['recipient_typization'])
    if col_map_dict['recipient_luminex_1'] is not None:
        col_map_dict['recipient_luminex_1'] = parse_hla(col_map_dict['recipient_luminex_1'])
    col_map_dict['recipient_luminex_2'] = parse_hla(col_map_dict['recipient_luminex_2'])

    return PatientPair(
        txm_event,
        **col_map_dict
    )


def parse_pairing_data(dir_path: str) -> pd.DataFrame:
    patient_pairs = []

    for config in PARSING_CONFIGS[:]:
        txm_event, header, sheet_name, nrows, col_map, filename = config

        path = os.path.join(dir_path, filename)
        df = pd.read_excel(path, index_col=None, header=header, sheet_name=sheet_name, nrows=nrows)

        if txm_event == 14:
            df = df.rename(columns={
                'Typing ': 'typing',
                'Typing': 'typing.1',
                'LUMINEX results': 'luminex varianta 2'  # This needs to be consulted with imunologists
            })
        if txm_event == 10:
            df['acceptable blood group'] = ''

        df = df.rename(columns=lambda x: x.lower())

        for _, row in df.iterrows():
            if col_map is None:
                continue
            pp = _row_to_patient_pair(row, config)
            if pp is not None:
                patient_pairs.append(pp)

    patient_pairs = [asdict(pp) for pp in patient_pairs]

    return pd.DataFrame(patient_pairs)
