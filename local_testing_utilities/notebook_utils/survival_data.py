import numpy as np
import pandas as pd

from local_testing_utilities.notebook_utils.utils import parse_hla


def _create_hlas(group_to_values):
    all_codes = ','.join([
        ','.join(
            [
                group + str(int(val))
                for val in str(values if not pd.isnull(values) else '').split(',')
                if len(val.strip()) > 0 and val != '-'
            ]
        )
        for group, values in group_to_values.items()
    ])
    return parse_hla(all_codes)


def _create_donor_typization(row):
    return _create_hlas({
        'A': row['Donor_HLAA'],
        'B': row['Donor_HLAB'],
        'Cw': row['Donor_HLACw'],
        'DP': row['Donor_HLADP'],
        'DQ': row['Donor_HLADQ'],
        'DR': row['Donor_HLADR']
    })


def _create_recipient_typization(row):
    return _create_hlas({
        'A': row['HLAA'],
        'B': row['HLAB'],
        'Cw': row['HLACw'],
        'DP': row['HLADP'],
        'DQ': row['HLADQ'],
        'DR': row['HLADR']
    })


def parse_survival_data(file_path: str) -> pd.DataFrame:
    df_survival = pd.read_csv(file_path)

    df_survival['donor_typization'] = df_survival.apply(_create_donor_typization, axis=1)
    df_survival['recipient_typization'] = df_survival.apply(_create_recipient_typization, axis=1)

    df_survival['StartDate'] = pd.to_datetime(df_survival['StartDate'])
    df_survival['LastVisitDate'] = pd.to_datetime(df_survival['LastVisitDate'])
    df_survival['EndDate'] = pd.to_datetime(df_survival['EndDate'])

    df_survival['delay'] = (df_survival['LastVisitDate'] - df_survival['StartDate']).dt.days

    df_survival = df_survival[[
        'RecipientID', 'StartDate', 'LastVisitDate', 'EndDate', 'delay', 'EndReason', 'NoVisits',
        'donor_typization', 'recipient_typization',
        'Donor_Sex', 'Donor_AgeAtTx', 'Donor_Weight', 'Donor_Height', 'Donor_EGFR', 'Donor_Info']]

    df_survival[['Donor_Weight', 'Donor_Height']] = df_survival[['Donor_Weight', 'Donor_Height']].replace({0: np.nan})

    return df_survival
