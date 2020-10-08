import pandas as pd

from txmatching.utils.get_absolute_path import get_absolute_path

PATH_TO_REL_DNA_SER = get_absolute_path('./txmatching/utils/hla_system/rel_dna_ser.txt')


def parse_rel_dna_ser(path_to_rel_dna_ser: str) -> pd.DataFrame:
    rel_dna_ser_df = (
        pd.read_csv(path_to_rel_dna_ser, comment='#', delimiter=';', header=None)

    )

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

    split_numbers = pd.concat([split_dp, split_unambiguous])

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


HIGH_RES_TO_SPLIT = {high_res: split if not pd.isna(split) else None for high_res, split in
                     parse_rel_dna_ser(PATH_TO_REL_DNA_SER).split.to_dict().items()}

SEROLOGICAL_CODES_IN_REL_DNA_SER = set(HIGH_RES_TO_SPLIT.values())
SEROLOGICAL_CODES_IN_REL_DNA_SER.remove(None)
