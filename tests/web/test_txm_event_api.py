from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmEventDTOIn, TxmEventUpdateDTOIn)
from txmatching.database.services.txm_event_service import get_txm_event_base
from txmatching.database.sql_alchemy_schema import (ConfigModel,
                                                    PairingResultModel,
                                                    RecipientModel,
                                                    TxmEventModel)
from txmatching.utils.enums import TxmEventState
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
            self.assertEqual('Invalid request data.', res.json['error'])
            self.assertEqual('missing value for field "name"', res.json['message'])

    def test_txm_event_deletion(self):
        self.fill_db_with_patients_and_results()
        txm_name = 'test'
        txm_event_model = TxmEventModel.query.filter(TxmEventModel.name == txm_name).first()
        self.assertEqual(1, len(txm_event_model.configs))
        self.assertIsNotNone(TxmEventModel.query.filter(TxmEventModel.name == txm_name).first())
        self.assertEqual(1, len(PairingResultModel.query.all()))

        self.login_with_role(UserRole.ADMIN)

        # Successful deletion
        with self.app.test_client() as client:
            res = client.delete(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_model.id}',
                headers=self.auth_headers
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)

        self.assertIsNone(TxmEventModel.query.filter(TxmEventModel.name == txm_name).first())
        self.assertEqual(0, len(PairingResultModel.query.all()))
        # Second deletion should fail
        with self.app.test_client() as client:
            res = client.delete(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_model.id}',
                headers=self.auth_headers
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)

    def test_txm_event_update(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()

        self.assertEqual(TxmEventState.OPEN, get_txm_event_base(txm_event_db_id).state)

        self.login_with_role(UserRole.ADMIN)

        # test changing state to CLOSED
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}',
                headers=self.auth_headers,
                json=TxmEventUpdateDTOIn(state=TxmEventState.CLOSED).__dict__
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual('CLOSED', res.json['state'])

        self.assertEqual(TxmEventState.CLOSED, get_txm_event_base(txm_event_db_id).state)

        # call api without changing anything
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}',
                headers=self.auth_headers,
                json=TxmEventUpdateDTOIn(state=None).__dict__
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual('CLOSED', res.json['state'])

        self.assertEqual(TxmEventState.CLOSED, get_txm_event_base(txm_event_db_id).state)

        # test changing state to OPEN
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}',
                headers=self.auth_headers,
                json=TxmEventUpdateDTOIn(state=TxmEventState.OPEN).__dict__
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual('OPEN', res.json['state'])

        self.assertEqual(TxmEventState.OPEN, get_txm_event_base(txm_event_db_id).state)

        # test non admin user
        self.login_with_role(UserRole.VIEWER)

        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event_db_id}',
                headers=self.auth_headers,
                json=TxmEventUpdateDTOIn(state=TxmEventState.CLOSED).__dict__
            )

            self.assertEqual(403, res.status_code)
            self.assertEqual('application/json', res.content_type)
