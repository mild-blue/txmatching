import json
import logging
import os
from enum import Enum

from dacite import Config, from_dict

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.database.services.patient_upload_service import (
    replace_or_add_patients_from_excel,
    replace_or_add_patients_from_one_country)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.web import create_app

logger = logging.getLogger(__name__)

# set the path here, the data is in Gdrive at the moment
PATH_TO_DATA_FOR_UPLOAD = 'path/to/data/for/upload'
TXM_EVENT_NAME = '2020-10-CZE-ISR-AUT'

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        txm_event_db_id = create_or_overwrite_txm_event(name=TXM_EVENT_NAME).db_id
        patients = parse_excel_data(os.path.join(PATH_TO_DATA_FOR_UPLOAD, 'czech_data.xlsx'),
                                    txm_event_name=TXM_EVENT_NAME, country=None)

        replace_or_add_patients_from_excel(patients)
        logger.info(f'successfully parsed czech patients')
        patients = parse_excel_data(os.path.join(PATH_TO_DATA_FOR_UPLOAD, 'austria_data.xlsx'),
                                    txm_event_name=TXM_EVENT_NAME, country=None)
        replace_or_add_patients_from_excel(patients)
        logger.info(f'successfully parsed austrian patients')

        with open(os.path.join(PATH_TO_DATA_FOR_UPLOAD, 'israel_data.json')) as json_file:
            data_json = json.load(json_file)

        patient_upload_dto = from_dict(data_class=PatientUploadDTOIn, data=data_json, config=Config(cast=[Enum]))
        replace_or_add_patients_from_one_country(patient_upload_dto)
        logger.info(
            f'successfully parsed israeli patients '
            f'{len(patient_upload_dto.donors) + len(patient_upload_dto.recipients)}')

        result = solve_from_configuration(txm_event_db_id=txm_event_db_id,
                                          configuration=Configuration(max_sequence_length=100, max_cycle_length=100,
                                                                      use_split_resolution=True))
        logger.info(f'Successfully stored {len(list(result.calculated_matchings_list))} matchings into the database.')
