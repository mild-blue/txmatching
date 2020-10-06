from typing import Dict

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from tests.web.data_upload_api.patient_upload_example_data import (
    TXM_EVENT_NAME, VALID_UPLOAD_1, VALID_UPLOAD_MISSING)
from txmatching.auth.data_types import UserRole
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.sql_alchemy_schema import UploadedDataModel
from txmatching.patients.patient import TxmEvent
from txmatching.patients.patient_parameters import HLAType, HLATyping
from txmatching.utils.blood_groups import BloodGroup
from txmatching.web import TXM_EVENT_NAMESPACE, txm_event_api


class TestMatchingApi(DbTests):

    def _upload_for_test(self, json: Dict) -> TxmEvent:
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
        return get_txm_event(txm_event.db_id)

    def test_txm_event_patient_successful_upload(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_1)

        self.assertEqual(1, len(UploadedDataModel.query.all()))
        self.assertEqual(1, txm_event.donors_dict[1].related_recipient_db_id)
        self.assertSetEqual({BloodGroup.ZERO, BloodGroup.A},
                            set(blood for blood in txm_event.recipients_dict[1].acceptable_blood_groups))
        self.assertEqual(HLATyping(hla_types_list=[HLAType(raw_code='A2', code='A2')]),
                         get_txm_event(txm_event.db_id).donors_dict[1].parameters.hla_typing)

    def test_txm_event_patient_successful_upload_missing_not_required_params(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_MISSING)
        self.assertIsNone(txm_event.recipients_dict[1].waiting_since)
