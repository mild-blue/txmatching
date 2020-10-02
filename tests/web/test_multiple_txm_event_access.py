from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.crypto.password_crypto import encode_password
from txmatching.auth.data_types import UserRole
from txmatching.auth.request_context import store_user_in_context
from txmatching.auth.user.totp import generate_totp_seed
from txmatching.database.services import txm_event_service
from txmatching.database.services.app_user_management import persist_user
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.web import PATIENT_NAMESPACE, patient_api


class TestMultipleEventAccess(DbTests):
    def test_txm_event_multiple(self):
        self.api.add_namespace(patient_api, path=f'/{PATIENT_NAMESPACE}')
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event_service.create_txm_event('test2')
        self.login_with_role(UserRole.ADMIN)
        with self.app.test_client() as client:
            self.assertEqual(0, len(client.get(f'/{PATIENT_NAMESPACE}/', headers=self.auth_headers).json['donors']))

        user = persist_user(AppUserModel(
            email='user_with_default_txm_event_set',
            pass_hash=encode_password('pwd'),
            role=UserRole.ADMIN,
            second_factor_material=generate_totp_seed(),
            require_2fa=False,
            default_txm_event_id=txm_event_db_id
        ))
        with self.app.test_client() as client:
            json = client.post('/user/login',
                               json={'email': user.email, 'password': 'pwd'}).json
            token = json['auth_token']
            self.auth_headers = {'Authorization': f'Bearer {token}'}
            store_user_in_context(user.id, user.role)

        with self.app.test_client() as client:
            self.assertEqual(2, len(client.get(f'/{PATIENT_NAMESPACE}/', headers=self.auth_headers).json['donors']))
