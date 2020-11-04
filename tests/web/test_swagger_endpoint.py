from tests.test_utilities.generate_swagger import PATH_TO_SWAGGER_YAML
from tests.test_utilities.populate_db import ADMIN_WITH_DEFAULT_TXM_EVENT
from tests.test_utilities.prepare_app import DbTests
from tests.test_utilities.swagger_testing.swagger_tester import swagger_test
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION


class TestTester(DbTests):

    def test_server_not_logged_in(self):
        with self.app.test_client() as client:
            swagger_test(swagger_yaml_path=PATH_TO_SWAGGER_YAML, app_client=client, use_example=True)

    def test_server_logged_in(self):
        self.txm_event_db_id = self.fill_db_with_patients(
            get_absolute_path('/tests/resources/patient_data_2020_07_obfuscated.xlsx')
        )
        authorize_error = {
            'post': {
                f'{API_VERSION}/user/otp': [403],
                f'{API_VERSION}/user/register': [200],
                f'{API_VERSION}/txm-event': [201]
            },
            'put': {
                f'{API_VERSION}/patients/donor': [200],
                f'{API_VERSION}/patients/recipient': [200]
            },
            'get': {
                f'{API_VERSION}/reports/{{matching_id}}': [200],
                f'{API_VERSION}/configuration': [200],
                f'{API_VERSION}/patients': [200],
                f'{API_VERSION}/user/refresh-token': [200],
                f'{API_VERSION}/service/version': [200],
            },
            'delete': {
                f'{API_VERSION}/txm-event/{{name}}': [200]
            }
        }
        # we need this user as we need the report to be generated from filled txm event, but we create an empty
        # txm event in the process of running the swagger
        self.login_with_credentials(ADMIN_WITH_DEFAULT_TXM_EVENT)
        with self.app.test_client() as client:
            # res = client.get('v1/reports/42?matchingsBelowChosen=42', headers=self.auth_headers)
            # self.assertEqual(200, res.status_code)
            swagger_test(swagger_yaml_path=PATH_TO_SWAGGER_YAML,
                         app_client=client,
                         use_example=True,
                         extra_headers=self.auth_headers,
                         authorize_error=authorize_error
                         )
