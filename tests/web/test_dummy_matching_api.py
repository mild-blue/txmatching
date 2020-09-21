from tests.test_utilities.prepare_app import DbTests
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import DUMMY_MATCHING_NAMESPACE, dummy_matching_api


class TestDummyMatchingApi(DbTests):

    def test_get_dummy_matching(self):
        self.fill_db_with_patients(get_absolute_path('/tests/test_utilities/data.xlsx'))
        self.api.add_namespace(dummy_matching_api, path=f'/{DUMMY_MATCHING_NAMESPACE}')

        with self.app.test_client() as client:
            solve_from_db()

            res = client.get(f'/{DUMMY_MATCHING_NAMESPACE}/')

            self.assertEqual(200, res.status_code)
            self.assertEqual("application/json", res.content_type)
            expected = [{'db_id': 1, 'score': 36.0, 'rounds': [{'transplants': [
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P21', 'recipient': 'P12'},
                {'score': 18.0, 'compatible_blood': True, 'donor': 'P22', 'recipient': 'P11'}]}],
                         'countries': [{'country_code': 'CZE', 'donor_count': 2, 'recipient_count': 2}]}]
            self.assertEqual(expected, res.json)
