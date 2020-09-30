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
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='unambigous')
    )

    done = set(split_unambigous.index)

    split_possible = (
        rel_dna_ser_df.loc[lambda df: set(df.index) - done, 3]
            .fillna('')
            .astype(str)
            .str.split('/')
            .str[-1]
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='possible')
    )

    done = set.union(done, split_possible.index)

    split_assumed = (
        rel_dna_ser_df.loc[lambda df: set(df.index) - done, 4]
            .fillna('')
            .astype(str)
            .str.replace('?', '')
            .str.replace('/?', '')
            .str.split('/')
            .str[-1]
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='assumed')
    )

    done = set.union(done, split_assumed.index)

    split_expert = (
        rel_dna_ser_df.loc[lambda df: set(df.index) - done, 5]
            .fillna('')
            .astype(str)
            .str.replace('?', '')
            .str.replace('/?', '')
            .str.split('/')
            .str[-1]
            .loc[lambda s: s != '']
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='expert')
    )

    done = set.union(done, split_expert.index)

    split_fallback = (
        rel_dna_ser_df.loc[lambda df: set(df.index) - done, 1]
            .str.split(':')
            .str[0]
            .str.replace('[A-Z]', '')
            .astype(int)
            .astype(str)
            .to_frame(name='split_number')
            .assign(source='fallback')
    )

    split_numbers = pd.concat([split_expert, split_assumed, split_fallback, split_possible, split_unambigous])

    rel_dna_ser_df['split_type'] = (rel_dna_ser_df[0]
                                    .str.replace(r'C\*', 'CW')
                                    .str.replace(r'(DQA1)|(DQB1)', 'DQ')
                                    .str.replace(r'(DPA1)|(DPB1)', 'DP')
                                    .str.replace(r'(DRB1)|(DRB3)|(DRB4)|(DRB5)|(DRA1)', 'DR')
                                    .str.replace(r'\*', '')
                                    )
    rel_dna_ser_df = rel_dna_ser_df.join(split_numbers)
    rel_dna_ser_df['split'] = rel_dna_ser_df['split_type'] + rel_dna_ser_df['split_number']
    rel_dna_ser_df = rel_dna_ser_df[['high_res', 'split', 'split_number', 'source']]
    rel_dna_ser_df = rel_dna_ser_df.set_index('high_res')
    return rel_dna_ser_df


HIGH_RES_TO_SPLIT = parse_rel_dna_ser().split.to_dict()

SPLIT_CODES = set(HIGH_RES_TO_SPLIT.values())
