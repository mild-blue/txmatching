from typing import Dict

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from tests.web.data_upload_api.patient_upload_example_data import (
    TXM_EVENT_NAME, VALID_UPLOAD_1)
from txmatching.auth.data_types import UserRole
from txmatching.database.sql_alchemy_schema import (DonorModel, RecipientModel,
                                                    UploadedDataModel)
from txmatching.patients.patient import TxmEvent
from txmatching.utils.enums import BloodGroup
from txmatching.web import TXM_EVENT_NAMESPACE, txm_event_api


class TestMatchingApi(DbTests):
    def test_mini(self):
        self.assertEqual(BloodGroup.A, BloodGroup('A'))
        self.assertEqual(BloodGroup.ZERO, BloodGroup(0))

    def upload_for_test(self, json: Dict) -> TxmEvent:
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        txm_event = create_or_overwrite_txm_event(name=TXM_EVENT_NAME)
        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=json
            )
        self.assertEqual(200, res.status_code)
        self.assertEqual('application/json', res.content_type)
        self.assertIsNotNone(res.json)
        self.assertLess(0, res.json['recipients_uploaded'])
        self.assertLess(0, res.json['donors_uploaded'])
        return txm_event

    def test_txm_event_patient_successful_upload(self):
        txm_event = self.upload_for_test(VALID_UPLOAD_1)
        donors = DonorModel.query.filter(DonorModel.txm_event_id == txm_event.db_id).all()
        recipients = RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event.db_id).all()

        self.assertEqual(1, len(donors))
        self.assertEqual(1, len(recipients))

        self.assertEqual(1, len(UploadedDataModel.query.all()))
        self.assertEqual(1, donors[0].recipient_id)
        self.assertSetEqual({'0', 'A'}, set(blood.blood_type for blood in recipients[0].acceptable_blood))
