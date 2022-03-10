import dataclasses

from local_testing_utilities.generate_patients import \
    store_generated_patients_from_folder
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.database.services.txm_event_service import (
    create_txm_event, get_txm_event_complete)
from txmatching.utils.country_enum import Country
from txmatching.utils.export.export_txm_event import \
    get_patients_upload_json_from_txm_event_for_country
from txmatching.web import API_VERSION, PUBLIC_NAMESPACE

UPLOADED_TXM_EVENT_NAME = 'test_upload'


class TestSaveAndGetConfiguration(DbTests):

    def test_get_matchings(self):
        txm_event_db_id = store_generated_patients_from_folder()

        txm_event = create_txm_event(UPLOADED_TXM_EVENT_NAME)
        to_upload_json = get_patients_upload_json_from_txm_event_for_country(txm_event_db_id.db_id, Country.CZE,
                                                                             UPLOADED_TXM_EVENT_NAME)
        self.assertEqual(len(to_upload_json.donors), 10)
        self.assertEqual(len(to_upload_json.recipients), 9)

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{PUBLIC_NAMESPACE}/patient-upload',
                headers=self.auth_headers,
                json=to_upload_json
            )
        self.assertEqual(res.status_code, 200)
        uploaded = get_txm_event_complete(txm_event.db_id, load_antibodies_raw=True)

        self.assertEqual(len(uploaded.all_donors), 10)
        self.assertEqual(len(uploaded.all_recipients), 9)
