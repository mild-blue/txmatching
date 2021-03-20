from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.patients.txm_event_dto_in import \
    TxmEventDTOIn
from txmatching.database.sql_alchemy_schema import (ConfigModel,
                                                    PairingResultModel,
                                                    RecipientModel,
                                                    TxmEventModel)
from txmatching.web import API_VERSION, TXM_EVENT_NAMESPACE


class TestMatchingApi(DbTests):

    def test_txm_event_creation_successful(self):

        txm_name = 'test2'

        self.login_with_role(UserRole.ADMIN)

        # Successful creation
        with self.app.test_client() as client:
            res = client.post(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}',
                headers=self.auth_headers,
                json=TxmEventDTOIn(name=txm_name).__dict__
            )

            self.assertEqual(201, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual(txm_name, res.json['name'])

        tmx_event_db = TxmEventModel.query.filter(TxmEventModel.name == txm_name).first()
        self.assertEqual(0, len(RecipientModel.query.filter(RecipientModel.txm_event_id == tmx_event_db.id).all()))
        self.assertEqual(0, len(ConfigModel.query.filter(ConfigModel.txm_event_id == tmx_event_db.id).all()))

        # Duplicate creation
        with self.app.test_client() as client:
            res = client.post(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}',
                headers=self.auth_headers,
                json=TxmEventDTOIn(name=txm_name).__dict__
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual('TXM event "test2" already exists.', res.json['message'])

    def test_txm_event_creation_failure_invalid_role(self):

        txm_name = 'test2'

        # VIEWER role
        self.login_with_role(UserRole.VIEWER)
        self._validate_invalid_access_for_event_creation(txm_name)

        # SERVICE role
        self.login_with_role(UserRole.SERVICE)
        self._validate_invalid_access_for_event_creation(txm_name)

    def _validate_invalid_access_for_event_creation(self, txm_name: str):
        with self.app.test_client() as client:
            res = client.post(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}',
                headers=self.auth_headers,
                json=TxmEventDTOIn(name=txm_name).__dict__
            )

            self.assertEqual(403, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)

    def test_txm_event_creation_invalid_data(self):

        self.login_with_role(UserRole.ADMIN)

        with self.app.test_client() as client:
            res = client.post(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}',
                headers=self.auth_headers,
                json={'invalid': 'data'}
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            # TODOO: comment
            #self.assertEqual('Invalid request data.', res.json['error'])
            #self.assertEqual('missing value for field "name"', res.json['message'])
            self.assertEqual('\'name\' is a required property', res.json['errors']['name'])
            self.assertEqual('Input payload validation failed', res.json['message'])

    def test_txm_event_deletion(self):
        self.fill_db_with_patients_and_results()
        txm_name = 'test'
        tmx_event_model = TxmEventModel.query.filter(TxmEventModel.name == txm_name).first()
        self.assertEqual(1, len(tmx_event_model.configs[0].pairing_results))
        self.assertIsNotNone(TxmEventModel.query.filter(TxmEventModel.name == txm_name).first())
        self.assertEqual(1, len(PairingResultModel.query.all()))

        self.login_with_role(UserRole.ADMIN)

        # Successful deletion
        with self.app.test_client() as client:
            res = client.delete(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_name}',
                headers=self.auth_headers
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)

        self.assertIsNone(TxmEventModel.query.filter(TxmEventModel.name == txm_name).first())
        self.assertEqual(0, len(PairingResultModel.query.all()))
        # Second deletion should fail
        with self.app.test_client() as client:
            res = client.delete(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_name}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
