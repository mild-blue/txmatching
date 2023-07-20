from typing import List

import pandas as pd

from txmatching.database.services.config_service import get_configuration_parameters_from_db_id_or_default
from txmatching.database.services.txm_event_service import get_txm_event_complete, get_txm_event_db_id_by_name
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.country_enum import Country
from txmatching.utils.hla_system.hla_crossmatch import is_positive_hla_crossmatch
from txmatching.web import create_app


def get_n_incompatible_pairs(txm_event_name: str) -> List[str | int]:
    txm_event_db_id = get_txm_event_db_id_by_name(txm_event_name)
    txm_event = get_txm_event_complete(txm_event_db_id)
    config_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, None)

    n_pairs = 0
    n_aboi_pairs = 0
    n_hlai_pairs = 0
    n_aboi_and_hlai_pairs = 0

    for donor in txm_event.all_donors:
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
    return [n_pairs, n_aboi_pairs, n_hlai_pairs, n_aboi_and_hlai_pairs, n_aboi_or_hlai_pairs]


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Specify txm events to compute the number of incompatible pairs for:
        txm_events_names = ['36-TXM-2022-01',
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
        df = pd.DataFrame(columns=['txm_event_name', 'n_pairs', 'n_aboi_pairs', 'n_hlai_pairs',
                                   'n_aboi_and_hlai_pairs', 'n_aboi_or_hlai_pairs'])

        for name in txm_events_names:
            df.loc[len(df)] = \
                [name] + get_n_incompatible_pairs(name)

    # Sum over all events
    sum_all_events = df.sum()
    sum_all_events.txm_event_name = 'all_events'
    df.loc[len(df)] = sum_all_events

    df.to_csv('aboi_hlai_report'
              '.csv', index=False)
