import json
import logging
from typing import Optional

import numpy as np

from txmatching.configuration.configuration import Configuration
from txmatching.database.services.matching_service import \
    get_matchings_detailed_for_configuration
from txmatching.database.services.txm_event_service import get_txm_event
from txmatching.patients.patient import DonorType
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.web import create_app

logger = logging.getLogger(__name__)

file = '/home/honza/graph.npy'
json_file = '/home/honza/patients_17_transplants.json'


def prepare_data(txm_event_db_id: int, top_configuration_id: Optional[int] = None):
    txm_event = get_txm_event(txm_event_db_id)
    configuration = Configuration(max_sequence_length=5, max_cycle_length=5,
                                  use_split_resolution=True, require_compatible_blood_group=False)
    scorer = scorer_from_configuration(configuration)
    donors_db_ids_to_ids = {donor.db_id: i for i, donor in enumerate(txm_event.active_donors_dict.values())}
    mat = []
    for donor in txm_event.active_donors_dict.values():
        row = []
        for donor_for_recipient in txm_event.active_donors_dict.values():

            if donor_for_recipient.related_recipient_db_id and donor.db_id != donor_for_recipient.db_id:
                recipient = txm_event.active_recipients_dict[donor_for_recipient.related_recipient_db_id]
                score = scorer._score_transplant_including_original_tuple(donor, recipient, donor_for_recipient)
                row.append(score)
            else:
                row.append(-1)

        mat.append(row)

    prepared_data = {}
    briding = [i for i, donor in enumerate(txm_event.active_donors_dict.values()) if
               donor.donor_type != DonorType.DONOR]
    prepared_data['briding'] = briding
    prepared_data['scores'] = mat
    donors_ids_to_medical_ids = {i: donor.medical_id for i, donor in enumerate(txm_event.active_donors_dict.values())}
    prepared_data['ids_to_medical'] = donors_ids_to_medical_ids

    if top_configuration_id is not None:
        result = get_matchings_detailed_for_configuration(txm_event, top_configuration_id).matchings[0]
        prepared_data['top_result'] = [
            [donors_db_ids_to_ids[pair.donor.db_id] for pair in round.donor_recipient_pairs] + [
                donors_db_ids_to_ids[round.donor_recipient_pairs[-1].recipient.related_donor_db_id]] for round in
            result.get_rounds()]

    with open(json_file, 'w') as f:
        json.dump(prepared_data, f, indent=4)

    np.save(file, mat)

    with open(json_file, 'w') as f:
        json.dump(prepared_data, f, indent=4)

    return prepared_data


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        prepared_data = prepare_data(2)
    print(prepared_data)
