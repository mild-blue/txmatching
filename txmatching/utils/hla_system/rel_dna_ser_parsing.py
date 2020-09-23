import pandas as pd

from txmatching.utils.get_absolute_path import get_absolute_path

PATH_TO_REL_DNA_SER = get_absolute_path('./txmatching/utils/hla_system/rel_dna_ser.txt')


def parse_rel_dna_ser():
    rel_dna_ser_df = (
        pd.read_csv(PATH_TO_REL_DNA_SER, comment='#', delimiter=';', header=None)

    )
    rel_dna_ser_df['high_res'] = rel_dna_ser_df[0] + rel_dna_ser_df[1]

    split = (
        rel_dna_ser_df.loc[:, [2, 3, 4, 5]]
            .fillna('')
            .astype(str)
            .sum(axis=1)
            .str.split('/')
            .str[0]
            .str.replace('?', '')
            .loc[lambda s: s != '']
            .astype(int)
    )

    rel_dna_ser_df['split'] = None
    rel_dna_ser_df['split_number'] = -1
    rel_dna_ser_df['split_type'] = rel_dna_ser_df[0].str.replace('*', '')
    rel_dna_ser_df.loc[split.index, 'split_number'] = split
    rel_dna_ser_df.loc[split.index, 'split'] = rel_dna_ser_df.loc[split.index, 'split_type'] + rel_dna_ser_df.loc[
        split.index, 'split_number'].astype(str)
    rel_dna_ser_df = rel_dna_ser_df[['high_res', 'split', 'split_number']]
    rel_dna_ser_df = rel_dna_ser_df.set_index('high_res')
    return rel_dna_ser_df.split.to_dict()


HIGH_RES_TO_SPLIT = parse_rel_dna_ser()
