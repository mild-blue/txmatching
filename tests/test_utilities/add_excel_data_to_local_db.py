import json
import logging
from enum import Enum

from dacite import Config, from_dict

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.upload_dto.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.database.services.patient_service import (
    save_patients_from_excel_to_txm_event, update_txm_event_patients)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        txm_event_db_id = create_or_overwrite_txm_event(name='2020-10-CZE-ISR-AUT').db_id
        patients = parse_excel_data('~/Downloads/VERSION_FOR_TXM_PROCESSING_PV31_revPR_Anon.xlsx')
        save_patients_from_excel_to_txm_event(patients, txm_event_db_id=txm_event_db_id)
        logging.info(f'successfully parsed czech patients {len(patients[0]) + len(patients[1])}')
        patients = parse_excel_data('~/Downloads/Vienna pairs, KPD 2020 Qu3, matchrun 24.xlsx')
        save_patients_from_excel_to_txm_event(patients, txm_event_db_id=txm_event_db_id)
        logging.info(f'successfully parsed austrian patients {len(patients[0]) + len(patients[1])}')
        with open('/home/honza/Downloads/israel_data.json') as json_file:
            data_json = json.load(json_file)

        patient_upload_dto = from_dict(data_class=PatientUploadDTOIn, data=data_json, config=Config(cast=[Enum]))
        country_code = patient_upload_dto.country
        update_txm_event_patients(patient_upload_dto, country_code)
        logging.info(
            f'successfully parsed israeli patients '
            f'{len(patient_upload_dto.donors) + len(patient_upload_dto.recipients)}')

        result = solve_from_configuration(txm_event_db_id=txm_event_db_id,
                                          configuration=Configuration(max_sequence_length=100, max_cycle_length=100,
                                                                      use_split_resolution=True))
        logger.info(f'Successfully stored {len(list(result.calculated_matchings))} matchings into the database.')
