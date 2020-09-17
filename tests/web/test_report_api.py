import dataclasses

from tests.test_utilities.prepare_app import DbTests
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import report_api, REPORTS_NAMESPACE


class TestMatchingApi(DbTests):

    def test_get_report(self):
        self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/data.xlsx'))
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')

        with self.app.test_client() as client:

            solve_from_db()

            res = client.get(f'/{REPORTS_NAMESPACE}/1?matchingRangeLimit=2', headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual("application/pdf", res.content_type)
            self.assertIsNotNone(res.data)
