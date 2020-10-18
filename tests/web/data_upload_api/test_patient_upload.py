from typing import Dict

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from tests.web.data_upload_api.patient_upload_example_data import (
    TXM_EVENT_NAME, VALID_UPLOAD_1, VALID_UPLOAD_EXCEPTIONAL_CODES,
    VALID_UPLOAD_MISSING_FIELDS, VALID_UPLOAD_MULTIPLE_SAME_HLA_CODES,
    VALID_UPLOAD_SPECIAL_HLA_CODES)
from txmatching.auth.data_types import UserRole
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.sql_alchemy_schema import UploadedDataModel, ParsingError
from txmatching.patients.patient import TxmEvent
from txmatching.patients.patient_parameters import HLAType, HLATyping
from txmatching.utils.blood_groups import BloodGroup
from txmatching.web import TXM_EVENT_NAMESPACE, txm_event_api


class TestMatchingApi(DbTests):

    def test_txm_event_patient_successful_upload(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_1)

        self.assertEqual(1, len(UploadedDataModel.query.all()))
        self.assertEqual(1, txm_event.donors_dict[1].related_recipient_db_id)
        self.assertSetEqual({BloodGroup.ZERO, BloodGroup.A},
                            set(blood for blood in txm_event.recipients_dict[1].acceptable_blood_groups))
        self.assertEqual(HLATyping(hla_types_list=[HLAType(raw_code='A2', code='A2')]),
                         get_txm_event(txm_event.db_id).donors_dict[1].parameters.hla_typing)
        self.assertListEqual(['A9'], txm_event.recipients_dict[1].hla_antibodies.hla_codes_over_cutoff)
        self._check_expected_errors_in_db(1)

    def test_txm_event_patient_successful_upload_missing_not_required_params(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_MISSING_FIELDS)
        self.assertIsNone(txm_event.recipients_dict[1].waiting_since)
        self._check_expected_errors_in_db(1)

    def test_txm_event_patient_successful_upload_special_hla_typing(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_SPECIAL_HLA_CODES)
        recipient = txm_event.recipients_dict[1]
        expected_antibodies = {'DPA1', 'DP4', 'A23'}
        self.assertSetEqual(expected_antibodies,
                            {hla_antibody.code for hla_antibody in
                             recipient.hla_antibodies.hla_antibodies_list})
        expected_typing = {'DQA1', 'A1', 'DQ6', 'B7'}
        self.assertSetEqual(expected_typing,
                            {hla_type.code for hla_type in
                             recipient.parameters.hla_typing.hla_types_list})
        self._check_expected_errors_in_db(0)

    def test_txm_event_patient_successful_upload_multiple_same_hla_types(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_MULTIPLE_SAME_HLA_CODES)
        recipient = txm_event.recipients_dict[1]
        expected_antibodies = {'DQA6', 'DQ8'}
        self.assertSetEqual(expected_antibodies, set(recipient.hla_antibodies.hla_codes_over_cutoff))
        self._check_expected_errors_in_db(0)

    def test_txm_event_patient_successful_upload_exceptional_hla_types(self):
        txm_event = self._upload_for_test(VALID_UPLOAD_EXCEPTIONAL_CODES)
        recipient = txm_event.recipients_dict[1]
        expected_antibodies = {'DR9', 'CW6', 'B82', 'CW4'}
        self.assertSetEqual(expected_antibodies, set(recipient.hla_antibodies.hla_codes_over_cutoff))

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

    def _check_expected_errors_in_db(self, expected_count: int):
        errors = ParsingError.query.all()
        self.assertEqual(expected_count, len(errors))
