from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.database.services.config_service import \
    save_configuration_to_db
from txmatching.database.services.pairing_result_service import \
    solve_from_config_id_and_save
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, REPORTS_NAMESPACE, TXM_EVENT_NAMESPACE
from txmatching.web.api.report_api import (INCLUDE_PATIENTS_SECTION_PARAM,
                                           MATCHINGS_BELOW_CHOSEN_PARAM,
                                           MAX_MATCHINGS_BELOW_CHOSEN,
                                           MIN_MATCHINGS_BELOW_CHOSEN)


class TestReportApi(DbTests):

    def test_get_matchings_report(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED)
        )
        txm_event = get_txm_event_complete(self.txm_event_db_id)
        configuration = Configuration()
        config_id = save_configuration_to_db(
            configuration=configuration,
            txm_event_id=txm_event.db_id,
            user_id=1
        )
        solve_from_config_id_and_save(
            config_id=config_id,
            configuration=configuration,
            txm_event=txm_event
        )

        # include param section
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                             f'{REPORTS_NAMESPACE}/configs/default/matchings/3/pdf'
                             f'?{MATCHINGS_BELOW_CHOSEN_PARAM}=2'
                             f'&{INCLUDE_PATIENTS_SECTION_PARAM}',
                             headers=self.auth_headers)

            self._assert_pdf_response_ok(res)

        # do not include param section
        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                             f'{REPORTS_NAMESPACE}/configs/default/matchings/3/pdf'
                             f'?{MATCHINGS_BELOW_CHOSEN_PARAM}=2',
                             headers=self.auth_headers)

            self._assert_pdf_response_ok(res)

    def test_patients_xlsx(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED)
        )
        txm_event = get_txm_event_complete(self.txm_event_db_id)
        configuration = Configuration()
        config_id = save_configuration_to_db(
            configuration=configuration,
            txm_event_id=txm_event.db_id,
            user_id=1
        )
        solve_from_config_id_and_save(
            config_id=config_id,
            configuration=configuration,
            txm_event=txm_event
        )

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                             f'{REPORTS_NAMESPACE}/configs/default/patients/xlsx',
                             headers=self.auth_headers)

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', res.content_type)
            self.assertIsNotNone(res.data)
            self.assertTrue(res.content_length > 0)
            self.assertIsNotNone(res.headers['x-filename'])

    def test_get_report_with_invalid_matching_id(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(self.txm_event_db_id)
        configuration = Configuration()
        config_id = save_configuration_to_db(
            configuration=configuration,
            txm_event_id=txm_event.db_id,
            user_id=1
        )
        solve_from_config_id_and_save(
            config_id=config_id,
            configuration=configuration,
            txm_event=txm_event
        )

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                             f'{REPORTS_NAMESPACE}/configs/default/matchings/6666/pdf?{MATCHINGS_BELOW_CHOSEN_PARAM}=2',
                             headers=self.auth_headers)

            self.assertEqual(401, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                'Matching with id 6666 not found.',
                res.json['message']
            )

    def test_get_report_with_invalid_matching_below_chosen_argument(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(self.txm_event_db_id)
        configuration = Configuration()
        config_id = save_configuration_to_db(
            configuration=configuration,
            txm_event_id=txm_event.db_id,
            user_id=1
        )
        solve_from_config_id_and_save(
            config_id=config_id,
            configuration=configuration,
            txm_event=txm_event
        )

        # Less than min value - failure
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                f'{REPORTS_NAMESPACE}/configs/default/'
                f'matchings/3/pdf?{MATCHINGS_BELOW_CHOSEN_PARAM}={MIN_MATCHINGS_BELOW_CHOSEN - 1}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                f'Query argument matchingsBelowChosen must be in range '
                f'[{MIN_MATCHINGS_BELOW_CHOSEN}, {MAX_MATCHINGS_BELOW_CHOSEN}].'
                f' Current value is {MIN_MATCHINGS_BELOW_CHOSEN - 1}.',
                res.json['message']
            )

        # More than max value - failure
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                f'{REPORTS_NAMESPACE}/configs/default/'
                f'matchings/3/pdf?{MATCHINGS_BELOW_CHOSEN_PARAM}={MAX_MATCHINGS_BELOW_CHOSEN + 1}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                f'Query argument matchingsBelowChosen must be in range '
                f'[{MIN_MATCHINGS_BELOW_CHOSEN}, {MAX_MATCHINGS_BELOW_CHOSEN}].'
                f' Current value is {MAX_MATCHINGS_BELOW_CHOSEN + 1}.',
                res.json['message']
            )

        # MIN_MATCHINGS_BELOW_CHOSEN - correct edge case
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                f'{REPORTS_NAMESPACE}/configs/default/'
                f'matchings/3/pdf?{MATCHINGS_BELOW_CHOSEN_PARAM}={MIN_MATCHINGS_BELOW_CHOSEN}',
                headers=self.auth_headers
            )

            self._assert_pdf_response_ok(res)

        # MAX_MATCHINGS_BELOW_CHOSEN - correct edge case
        with self.app.test_client() as client:
            res = client.get(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{self.txm_event_db_id}/'
                f'{REPORTS_NAMESPACE}/configs/default/'
                f'matchings/3/pdf?{MATCHINGS_BELOW_CHOSEN_PARAM}={MAX_MATCHINGS_BELOW_CHOSEN}',
                headers=self.auth_headers
            )

            self._assert_pdf_response_ok(res)

    def _assert_pdf_response_ok(self, res):
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/pdf', res.content_type)
        self.assertIsNotNone(res.data)
        self.assertTrue(res.content_length > 0)
        self.assertIsNotNone(res.headers['x-filename'])
