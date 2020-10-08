from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import REPORTS_NAMESPACE, report_api
from txmatching.web.api.report_api import MATCHINGS_BELOW_CHOSEN


class TestMatchingApi(DbTests):

    def test_get_report(self):
        self.txm_event_db_id = self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/patient_data_2020_07_obfuscated.xlsx'))
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')

        with self.app.test_client() as client:
            solve_from_db(Configuration(), self.txm_event_db_id)

            res = client.get(f'/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}=2', headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/pdf', res.content_type)
            self.assertIsNotNone(res.data)
            self.assertTrue(res.content_length > 0)
            self.assertIsNotNone(res.headers['x-filename'])
