# pylint: disable-all
import csv

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from txmatching.database.services.config_service import get_configuration_parameters_from_db_id_or_default
from txmatching.database.services.txm_event_service import get_txm_event_complete, get_txm_event_db_id_by_name
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLAAntibodyType, DQDPChain, HLAGroup
from txmatching.utils.hla_system.hla_crossmatch import is_positive_hla_crossmatch
from txmatching.web import create_app
from txmatching.utils.hla_system.compatibility_index import _which_dq_dp_chain


HIGHLY_SENSITIZED_TH = 90.0
VERY_HIGHLY_SENSITIZED_TH = 97.0


def calculate_n_incompatible_pairs(txm_event):
    config_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, None)

    n_pairs = 0
    n_aboi_pairs = 0
    n_hlai_pairs = 0
    n_aboi_and_hlai_pairs = 0

    print('Computing incompatible pairs')
    for donor in tqdm(txm_event.all_donors):
        if donor.parameters.country_code not in [Country.CZE, Country.ISR, Country.AUT]:
            continue

        if donor.related_recipient_db_id and donor.db_id in txm_event.active_and_valid_donors_dict:
            # Valid donor - related recipient pair
            n_pairs += 1
            related_recipient = next(recipient for recipient in txm_event.all_recipients if
                                     recipient.db_id == donor.related_recipient_db_id)
            is_aboi, is_hlai = False, False

            # Test ABOi
            if not blood_groups_compatible(donor.parameters.blood_group, related_recipient.parameters.blood_group):
                is_aboi = True
                n_aboi_pairs += 1

            # Test HLAi
            if is_positive_hla_crossmatch(donor_hla_typing=donor.parameters.hla_typing,
                                          recipient_antibodies=related_recipient.hla_antibodies,
                                          use_high_resolution=config_parameters.use_high_resolution,
                                          crossmatch_level=config_parameters.hla_crossmatch_level):
                is_hlai = True
                n_hlai_pairs += 1

            if is_aboi and is_hlai:
                n_aboi_and_hlai_pairs += 1

    n_aboi_or_hlai_pairs = n_aboi_pairs + n_hlai_pairs - n_aboi_and_hlai_pairs
    return n_pairs, n_aboi_pairs, n_hlai_pairs, n_aboi_and_hlai_pairs, n_aboi_or_hlai_pairs


def comput_vpra(unacceptable_antibodies):
    url = 'https://www.etrl.org/calculator4.0/calculator4.0.asmx'
    headers = {'content-type': 'text/xml'}

    body = \
        f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <VirtualPRA xmlns="http://ETRL.ORG/">
                        <sUserName>find-it-in-bitwarden</sUserName>
                        <sPassWord>find-it-in-bitwarden</sPassWord>
                        <sUnacceptables>{', '.join(unacceptable_antibodies)}</sUnacceptables>
                    </VirtualPRA>
                </soap:Body>
            </soap:Envelope>
            """

    response = requests.post(url, data=body, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    # print(soup.find('frequency'))
    vpra = float(soup.find('frequency').get_text())

    # print(soup.find('matches'))

    # print(soup.find('panelsize'))

    # print(soup.find('errormessage'))

    return vpra


def calculate_highly_sensitized_recipients(txm_event):
    vpras = []
    print('Computing vpras')
    for recipient in tqdm(txm_event.all_recipients):
        if recipient.db_id in txm_event.active_and_valid_recipients_dict:
            unacceptable_antibodies = []
            for antibodies_group in recipient.hla_antibodies.hla_antibodies_per_groups:
                for antibody in antibodies_group.hla_antibody_list:
                    if antibody.type == HLAAntibodyType.NORMAL and \
                            antibody.second_code is None and \
                            antibody.mfi > antibody.cutoff:

                        # Solve different nomenclature of DPA, DQA, DPB
                        if antibodies_group.hla_group in [HLAGroup.DP, HLAGroup.DQ] and \
                                not antibody.code.is_in_high_res():

                            dq_dp_chain = _which_dq_dp_chain(antibody)

                            if dq_dp_chain == DQDPChain.BETA_DP:
                                hla_number = antibody.code.broad[2:]

                                if len(hla_number) == 1:
                                    unacceptable_antibodies.append(('DP-0' + hla_number))
                                elif len(hla_number) == 2:
                                    unacceptable_antibodies.append(('DP-' + hla_number))
                                else:
                                    raise AssertionError

                                if unacceptable_antibodies[-1] == 'DP-02':
                                    unacceptable_antibodies[-1] = 'DP-0201'
                                    unacceptable_antibodies.append('DP-0202')

                                if unacceptable_antibodies[-1] == 'DP-04':
                                    unacceptable_antibodies[-1] = 'DP-0401'
                                    unacceptable_antibodies.append('DP-0402')

                            elif dq_dp_chain in [DQDPChain.ALPHA_DP, DQDPChain.ALPHA_DQ]:
                                hla_number = antibody.code.broad[2:]
                                if len(hla_number) == 1:
                                    unacceptable_antibodies.append((dq_dp_chain + '-0' + hla_number))
                                elif len(hla_number) == 2:
                                    unacceptable_antibodies.append((dq_dp_chain + '-' + hla_number))
                                else:
                                    raise AssertionError

                            else:
                                # DQB
                                unacceptable_antibodies.append(antibody.code.display_code)

                            print(f'Parsed {antibody.raw_code} -> {unacceptable_antibodies[-2:]}')

                        # All other loci are used with the same nomencalture we use
                        else:
                            unacceptable_antibodies.append(antibody.code.display_code)

            # print(f'{recipient.medical_id=}')
            # print(f'{unacceptable_antibodies=}')
            vpras.append(comput_vpra(unacceptable_antibodies))
            # print()

    n_highly_sensitized = (np.array(vpras) > HIGHLY_SENSITIZED_TH).sum()
    n_very_highly_sensitized = (np.array(vpras) > VERY_HIGHLY_SENSITIZED_TH).sum()
    return n_highly_sensitized, n_very_highly_sensitized, vpras


def compute_report(txm_events_names):

    df = pd.DataFrame(columns=['txm_event_name', 'n_pairs', 'n_aboi_pairs', 'n_hlai_pairs',
                               'n_aboi_and_hlai_pairs', 'n_aboi_or_hlai_pairs', 'n_highly_sensitized_recipients',
                               'n_very_highly_sensitized_recipients'])

    list_of_vpras = []

    for i, txm_event_name in enumerate(txm_events_names):
        print(f'[{i+1}/{len(txm_events_names)}] Computing report for {txm_event_name}')
        txm_event_db_id = get_txm_event_db_id_by_name(txm_event_name)
        txm_event = get_txm_event_complete(txm_event_db_id)

        n_pairs, n_aboi_pairs, n_hlai_pairs, n_aboi_and_hlai_pairs, n_aboi_or_hlai_pairs = \
            calculate_n_incompatible_pairs(txm_event)
        n_highly_sensitized, n_very_highly_sensitized, vpras = calculate_highly_sensitized_recipients(txm_event)
        list_of_vpras.append([txm_event_name] + vpras)

        df.loc[len(df)] = \
            [txm_event_name, n_pairs, n_aboi_pairs, n_hlai_pairs, n_aboi_and_hlai_pairs, n_aboi_or_hlai_pairs,
             n_highly_sensitized, n_very_highly_sensitized]

    df.to_csv('aboi_hlai_vpra_report.csv', index=False)

    with open('vpras.csv', "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(list_of_vpras)


if __name__ == '__main__':
    # Specify txm events to compute the number of incompatible pairs for:
    txm_events = ['36-TXM-2022-01',
                  '2020-10-CZE-ISR-AUT',
                  '2021-01-CZE-ISR-AUT',
                  '2020-07-CZE-ISR-AUT',
                  '37-TXM-2022-04',
                  '38-TXM-2022-07',
                  '33-TXM-2021-04-v2',
                  '33-TXM-2021-04',
                  '39-TXM-2022-10',
                  '34-TXM-2021-07',
                  '35-TXM-2021-10',
                  '40-TXM-2023-01',
                  '41-TXM-2023-04',
                  '42-TXM-2023-07']

    # txm_events = ['high_res_example_data', 'mock_data_CZE_CAN_IND']
    # txm_events = ['mock_data_CZE_CAN_IND']
    app = create_app()
    with app.app_context():
        compute_report(txm_events)
