from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.database.services import txm_event_service
from txmatching.web import API_VERSION, PATIENT_NAMESPACE, TXM_EVENT_NAMESPACE


class TestMultipleEventAccess(DbTests):
    def test_txm_event_multiple(self):
        txm_event_1_db_id = self.fill_db_with_patients_and_results()
        txm_event_2_db_id = txm_event_service.create_txm_event('test2').db_id
        self.login_with_role(UserRole.ADMIN)
        with self.app.test_client() as client:
            self.assertEqual(2, len(
                client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_1_db_id}/'
                           f'{PATIENT_NAMESPACE}/configs/default',
                           headers=self.auth_headers).json['donors']))
            self.assertEqual(0, len(
                client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_2_db_id}/'
                           f'{PATIENT_NAMESPACE}/configs/default',
                           headers=self.auth_headers).json['donors']))
