import pandas as pd

from txmatching.utils.get_absolute_path import get_absolute_path

PATH_TO_REL_DNA_SER = get_absolute_path('./txmatching/utils/hla_system/rel_dna_ser.txt')


def parse_rel_dna_ser():
    rel_dna_ser_df = (
        pd.read_csv(PATH_TO_REL_DNA_SER, comment='#', delimiter=';', header=None)

    )

    rel_dna_ser_df['high_res'] = rel_dna_ser_df[0] + rel_dna_ser_df[1]

    split_unambigous = (
        rel_dna_ser_df[2]
            .fillna('')
            .astype(str)
            .replace('?', '')
            .replace('0', '')
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='unambigous')
    )

    split_dp = (
        rel_dna_ser_df.loc[lambda df: rel_dna_ser_df[0].str.startswith('DP'), 1]
            .str.split(':')
            .str[0]
            # remove special ones with letter - we do not know what code to assign to them
            .loc[lambda s: ~s.str.contains('[A-Z]')]
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='dp_fallback')
    )

    split_numbers = pd.concat([split_dp, split_unambigous])

    rel_dna_ser_df['split_type'] = (rel_dna_ser_df[0]
                                    # gene codes to serology codes as aggreed with immunologists
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
                     parse_rel_dna_ser().split.to_dict().items()}

SPLIT_CODES = set(HIGH_RES_TO_SPLIT.values())
