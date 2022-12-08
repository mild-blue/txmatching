import re

import pandas as pd

from txmatching.utils.enums import HLA_GROUPS_PROPERTIES, HLAGroup
from txmatching.utils.get_absolute_path import get_absolute_path

PATH_TO_REL_DNA_SER = get_absolute_path('./txmatching/utils/hla_system/rel_dna_ser.txt')


def parse_rel_dna_ser(path_to_rel_dna_ser: str) -> pd.DataFrame:
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
            .str.split('/')
            .apply(lambda s: [x for x in s if x not in ['0', '?']])
            .apply(lambda s: s[0] if len(s) == 1 else '')
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
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
                                    .str.replace(r'C\*', 'CW', regex=True)
                                    .str.replace(r'DQB1', 'DQ', regex=True)
                                    .str.replace(r'DQA1', 'DQA', regex=True)
                                    .str.replace(r'DPB1', 'DP', regex=True)
                                    .str.replace(r'DPA1', 'DPA', regex=True)
                                    .str.replace(r'(DRB1)|(DRB3)|(DRB4)|(DRB5)|(DRA1)', 'DR',
                                                 regex=True)
                                    .str.replace(r'\*', '', regex=True)
                                    )
    rel_dna_ser_df = rel_dna_ser_df.join(split_numbers)
    rel_dna_ser_df['split'] = rel_dna_ser_df['split_type'] + rel_dna_ser_df['split_number']
    rel_dna_ser_df = rel_dna_ser_df[['high_res', 'split', 'split_number', 'source']]
    rel_dna_ser_df = rel_dna_ser_df.set_index('high_res')
    return rel_dna_ser_df


def _matches_any_hla_group(high_res: str) -> bool:
    return re.match(HLA_GROUPS_PROPERTIES[HLAGroup.ALL].high_res_code_regex, high_res) is not None
