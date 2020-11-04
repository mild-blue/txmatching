from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services import solver_service
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, REPORTS_NAMESPACE
from txmatching.web.api.report_api import (MATCHINGS_BELOW_CHOSEN,
                                           MAX_MATCHINGS_BELOW_CHOSEN,
                                           MIN_MATCHINGS_BELOW_CHOSEN)


class TestMatchingApi(DbTests):

    def test_get_report(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx')
        )
        pairing_result = solve_from_configuration(Configuration(), self.txm_event_db_id)
        solver_service.save_pairing_result(pairing_result)

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}=2',
                             headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/pdf', res.content_type)
            self.assertIsNotNone(res.data)
            self.assertTrue(res.content_length > 0)
            self.assertIsNotNone(res.headers['x-filename'])

    def test_get_report_with_invalid_matching_id(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'))
        pairing_result = solve_from_configuration(Configuration(), self.txm_event_db_id)
        solver_service.save_pairing_result(pairing_result)

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{REPORTS_NAMESPACE}/6666?{MATCHINGS_BELOW_CHOSEN}=2',
                             headers=self.auth_headers)

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                'Matching with id 6666 not found.',
                res.json['message']
            )

    def test_get_report_with_invalid_matching_below_chosen_argument(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx'))
        pairing_result = solve_from_configuration(Configuration(), self.txm_event_db_id)
        solver_service.save_pairing_result(pairing_result)

        # Less than min value - failure
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}={MIN_MATCHINGS_BELOW_CHOSEN - 1}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                'Query argument matchingsBelowChosen must be in range [0, 100]. Current value is -1.',
                res.json['message']
            )

        # More than max value - failure
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}={MAX_MATCHINGS_BELOW_CHOSEN + 1}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                'Query argument matchingsBelowChosen must be in range [0, 100]. Current value is 101.',
                res.json['message']
            )

        # MIN_MATCHINGS_BELOW_CHOSEN - correct edge case
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}={MIN_MATCHINGS_BELOW_CHOSEN}',
                headers=self.auth_headers
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/pdf', res.content_type)
            self.assertIsNotNone(res.data)
            self.assertTrue(res.content_length > 0)
            self.assertIsNotNone(res.headers['x-filename'])

        # MAX_MATCHINGS_BELOW_CHOSEN - correct edge case
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{REPORTS_NAMESPACE}/298?{MATCHINGS_BELOW_CHOSEN}={MAX_MATCHINGS_BELOW_CHOSEN}',
                headers=self.auth_headers
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/pdf', res.content_type)
            self.assertIsNotNone(res.data)
            self.assertTrue(res.content_length > 0)
            self.assertIsNotNone(res.headers['x-filename'])
