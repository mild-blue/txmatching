import dataclasses
import json
import logging
import os

from txmatching.utils.country_enum import Country
from txmatching.utils.excel_parsing.parse_excel_data import (ExcelSource,
                                                             parse_excel_data)
from txmatching.web import create_app

logger = logging.getLogger(__name__)

# set the path here to excel with data
PATH_TO_DATA_FOR_UPLOAD = '/home/honza/Downloads/LDEP KUL - UCL July 22..xlsx'
TXM_EVENT_NAME = 'TEST-BEL-PRIVATE-2022-02'


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        patients = parse_excel_data(os.path.join(PATH_TO_DATA_FOR_UPLOAD),
                                    txm_event_name=TXM_EVENT_NAME,
                                    country=Country.BEL_2,
                                    excel_source=ExcelSource.BEL_2
                                    )
        # here we are assuming currently for simplicity that the data is from one country only
        patients_together = patients[0]
        patients_together.add_to_existing_patients = False
        for patient in patients[1:]:
            patients_together.donors += patient.donors
            patients_together.recipients += patient.recipients

        with open('tmp.json', 'w', encoding='utf-8') as f:
            json.dump(dataclasses.asdict(patients_together), f)
