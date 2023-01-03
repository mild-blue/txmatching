from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.data_transfer_objects.patients.txm_event_dto_in import (
    TxmEventCopyPatientsDTOIn, TxmEventDTOIn, TxmEventUpdateDTOIn)
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import get_txm_event_base, get_txm_event_complete
from txmatching.database.sql_alchemy_schema import (ConfigModel, DonorModel,
                                                    PairingResultModel,
                                                    RecipientModel,
                                                    TxmEventModel)
from txmatching.patients.patient import DonorType
from txmatching.utils.enums import StrictnessType, TxmEventState
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.web import API_VERSION, PATIENT_NAMESPACE, TXM_EVENT_NAMESPACE

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

    def test_txm_event_copy_patients_between_events(self):
        txm_event_model_from_db_id = self.fill_db_with_patients()
        txm_event_model_to = create_or_overwrite_txm_event(name='test_copy')

        self.assertIsNotNone(TxmEventModel.query.get(txm_event_model_from_db_id))
        self.assertIsNotNone(TxmEventModel.query.get(txm_event_model_to.db_id))

        donors = TxmEventModel.query.get(txm_event_model_from_db_id).donors
        donor_ids = [donor.id for donor in donors]

        self.login_with_role(UserRole.ADMIN)

        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/copy',
                headers=self.auth_headers,
                json=TxmEventCopyPatientsDTOIn(
                    txm_event_id_from=txm_event_model_from_db_id,
                    txm_event_id_to=txm_event_model_to.db_id,
                    donor_ids=donor_ids
                ).__dict__
            )

            self.assertIsNotNone(res.json['new_donor_ids'])
            self.assertEqual(len(donor_ids), len(res.json['new_donor_ids']))

            for donor_id in res.json['new_donor_ids']:
                self.assertIsNotNone(DonorModel.query.get(donor_id))

            self.assertEqual(
                len(res.json['new_donor_ids']),
                len(TxmEventModel.query.get(txm_event_model_to.db_id).donors)
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)

    def test_txm_event_copy_between_events_not_working(self):
        txm_event_model_from_db_id = self.fill_db_with_patients(
            get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event_model_to = create_or_overwrite_txm_event(name='test_copy')

        donor_ids = [14, 15]

        self.login_with_role(UserRole.ADMIN)

        # alter donor table so that there's 2 donors relating to the same recipient
        donor_id_to_change = 15
        recipient_id_for_error = 13
        DonorModel.query.filter(DonorModel.id == donor_id_to_change).update(
            {'recipient_id': recipient_id_for_error})
        db.session.commit()

        # copy patients from txm_event_from to txm_event_to
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/copy',
                headers=self.auth_headers,
                json=TxmEventCopyPatientsDTOIn(
                    txm_event_id_from=txm_event_model_from_db_id,
                    txm_event_id_to=txm_event_model_to.db_id,
                    donor_ids=donor_ids
                ).__dict__
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)

        # test for the case when three donors have the same recipient and they are copied in the separate endpoint calls
        donor_ids_to_change = [17, 18]
        recipient_id_for_error = 15

        for donor_id in donor_ids_to_change:
            DonorModel.query.filter(DonorModel.id == donor_id).update(
                {'recipient_id': recipient_id_for_error})
        db.session.commit()

        # copy two donors
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/copy',
                headers=self.auth_headers,
                json=TxmEventCopyPatientsDTOIn(
                    txm_event_id_from=txm_event_model_from_db_id,
                    txm_event_id_to=txm_event_model_to.db_id,
                    donor_ids=donor_ids_to_change
                ).__dict__
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(DonorModel.query.get(res.json['new_donor_ids'][0]).recipient_id)
            self.assertIsNotNone(DonorModel.query.get(res.json['new_donor_ids'][1]).recipient_id)

        # copy the remaining donor and assert that we get the error
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/copy',
                headers=self.auth_headers,
                json=TxmEventCopyPatientsDTOIn(
                    txm_event_id_from=txm_event_model_from_db_id,
                    txm_event_id_to=txm_event_model_to.db_id,
                    donor_ids=[16]
                ).__dict__
            )

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)
            self.assertEqual('Recipient with medical id 130B-CZE-R already exists in event test_copy. Unfortunately,'
                             ' we do not support copying donors with the related recipient that is already in '
                             'TxmEventTo yet.',
                             res.json['message'])

    def test_forgiving_txm_event(self):
        donor_medical_id = 'donor_test'
        recipient_medical_id = 'recipient_test'
        invalid_pair = {
                'donor': {
                    'medical_id': donor_medical_id,
                    'blood_group': 'A',
                    'hla_typing': [],
                    'donor_type': DonorType.DONOR.value,
                },
                'recipient': {
                    'medical_id': recipient_medical_id,
                    'acceptable_blood_groups': [],
                    'blood_group': 'A',
                    'hla_typing': [],
                    'recipient_cutoff': 2000,
                    'hla_antibodies': [],
                },
                'country_code': 'CZE'
            }

        # strict event
        txm_event = create_or_overwrite_txm_event(name='test', strictness_type=StrictnessType.STRICT)
        with self.app.test_client() as client:
            client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event.db_id}/'
                        f'{PATIENT_NAMESPACE}/pairs',
                        headers=self.auth_headers, json=invalid_pair)

        txm_event = get_txm_event_complete(txm_event.db_id)
        self.assertNotEqual(len(txm_event.all_donors), len(txm_event.active_and_valid_donors_dict))
        self.assertNotEqual(len(txm_event.all_recipients), len(txm_event.active_and_valid_recipients_dict))

        # forgiving event
        txm_event = create_or_overwrite_txm_event(name='test', strictness_type=StrictnessType.FORGIVING)
        with self.app.test_client() as client:
            client.post(f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/{txm_event.db_id}/'
                        f'{PATIENT_NAMESPACE}/pairs',
                        headers=self.auth_headers, json=invalid_pair)

        txm_event = get_txm_event_complete(txm_event.db_id)
        self.assertEqual(len(txm_event.all_donors), len(txm_event.active_and_valid_donors_dict))
        self.assertEqual(len(txm_event.all_recipients), len(txm_event.active_and_valid_recipients_dict))
