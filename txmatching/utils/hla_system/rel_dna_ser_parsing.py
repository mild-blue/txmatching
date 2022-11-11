import re
from typing import Dict, List

import pandas as pd

from txmatching.utils.enums import HLA_GROUPS_PROPERTIES, HLAGroup
from txmatching.utils.get_absolute_path import get_absolute_path

PATH_TO_REL_DNA_SER = get_absolute_path('./txmatching/utils/hla_system/rel_dna_ser.txt')


def parse_rel_dna_ser(path_to_rel_dna_ser: str, are_multiple_values_allowed: bool = False) -> pd.DataFrame:
    rel_dna_ser_df = (
        pd.read_csv(path_to_rel_dna_ser, comment='#', delimiter=';', header=None)

    )

    rel_dna_ser_df = rel_dna_ser_df.loc[lambda df: df[0].apply(_matches_any_hla_group)]

    rel_dna_ser_df['high_res'] = rel_dna_ser_df[0] + rel_dna_ser_df[1]

    split_unambiguous = (
        rel_dna_ser_df[2]
            .fillna('')
            .astype(str)
            .replace('?', '')
            .replace('0', '')
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='unambiguous')
    )

    split_assumed = (
        rel_dna_ser_df[4]
            .fillna('')
            .astype(str)
            .loc[lambda s: s != '']
            .loc[lambda s: are_multiple_values_allowed | ~s.str.contains('/')]
            .loc[lambda s: ~s.str.contains('^0')]
            .to_frame(name='split_number')
            .assign(source='assumed')
    )

    split_dp = (
        rel_dna_ser_df
            .loc[lambda df: ~df.index.isin(split_unambiguous.index) & (df[2] == '?')]
            .loc[lambda df: (rel_dna_ser_df[0].str.startswith('DP')) |
                            (rel_dna_ser_df[0].str.startswith('C*')) |
                            (rel_dna_ser_df[0].str.startswith('DQA')), 1]
            .str.split(':')
            .str[0]
            # remove special ones with letter - we do not know what code to assign to them
            .loc[lambda s: ~s.str.contains('[A-Z]')]
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='dp_cw_fallback')
    )

    split_numbers = pd.concat([split_dp, split_unambiguous, split_assumed])

    rel_dna_ser_df['split_type'] = (rel_dna_ser_df[0]
                                    # gene codes to serology codes as agreed with immunologists
                                    .str.replace(r'C\*', 'CW')
                                    .str.replace(r'DQB1', 'DQ')
                                    .str.replace(r'DQA1', 'DQA')
                                    .str.replace(r'DPB1', 'DP')
                                    .str.replace(r'DPA1', 'DPA')
                                    .str.replace(r'(DRB1)|(DRB3)|(DRB4)|(DRB5)|(DRA1)', 'DR')
                                    .str.replace(r'\*', '')
                                    )
    rel_dna_ser_df = rel_dna_ser_df.join(split_numbers)
    rel_dna_ser_df['split'] = rel_dna_ser_df['split_type'] + rel_dna_ser_df['split_number']
    rel_dna_ser_df = rel_dna_ser_df[['high_res', 'split', 'split_number', 'source']]
    rel_dna_ser_df = rel_dna_ser_df.set_index('high_res')
    return rel_dna_ser_df


def get_multiple_serological_codes_from_rel_dna_ser_df(rel_dna_ser_df: pd.DataFrame) -> \
        Dict[str, List[str]]:
    """
    :param rel_dna_ser_df: pd.Dataframe, which contains multiple splits in n/m format (example B15/70).
                           Usually is recived from parse_rel_dna_ser(..., are_multiple_values_allowed=True)
    :return: {high_res: list of corresponding serological codes, ...} from rel_dna_ser_df.
    """
    assert 'split' in rel_dna_ser_df.columns and 'split_number' in rel_dna_ser_df.columns, \
        'Wrong dataframe format for this method. Columns high_res and split are needed.'

    split_types = rel_dna_ser_df.split.where(lambda s: s.str.contains('/')).dropna()\
        .replace('[0-9/]', '', regex=True).to_dict()
    split_nums = rel_dna_ser_df.split_number.where(lambda s: s.str.contains('/')).dropna()\
        .str.split('/').to_dict()

    return {high_res: [split_type + split_num for split_num in split_nums[high_res]]
            for high_res, split_type in split_types.items()}


def _matches_any_hla_group(high_res: str) -> bool:
    return re.match(HLA_GROUPS_PROPERTIES[HLAGroup.ALL].high_res_code_regex, high_res) is not None
