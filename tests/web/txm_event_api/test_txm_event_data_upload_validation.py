from typing import Dict, List, Optional, Set, Tuple

from flask import Response

from tests.test_utilities.prepare_app import DbTests
from tests.web.txm_event_api.txm_event_upload_example_data import (
    DONORS, RECIPIENTS,
    SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_EXISTING_RECIPIENT_ID,
    SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_MISSING_RECIPIENT_ID,
    SPECIAL_DONORS_DUPLICATED_RECIPIENT_MEDICAL_IDS,
    SPECIAL_DONORS_INVALID_RECIPIENT_MEDICAL_ID,
    SPECIAL_DONORS_SPECIAL_HLA_CODES, SPECIAL_RECIPIENTS_EXCEPTIONAL_HLA_CODES,
    SPECIAL_RECIPIENTS_MULTIPLE_SAME_HLA_CODES,
    SPECIAL_RECIPIENTS_SPECIAL_HLA_CODES,
    SPECIAL_RECIPIENTS_WAITING_SINCE_DATE_INVALID)
from txmatching.auth.data_types import UserRole
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import (
    get_newest_txm_event_db_id, get_txm_event)
from txmatching.database.sql_alchemy_schema import (ParsingErrorModel,
                                                    UploadedDataModel)
from txmatching.patients.patient import Patient, Recipient, TxmEvent
from txmatching.patients.patient_parameters import HLATyping
from txmatching.patients.patient_parameters_dataclasses import HLAType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country
from txmatching.web import API_VERSION, TXM_EVENT_NAMESPACE


class TestMatchingApi(DbTests):

    def test_txm_event_patient_successful_upload(self):
        res, txm_event = self._txm_event_upload(donors_json=DONORS, recipients_json=RECIPIENTS)
        self._check_response(res, 200)
        txm_event = get_txm_event(txm_event.db_id)
        self.assertEqual(txm_event.name, txm_event.name)
        self.assertEqual(3, len(txm_event.active_recipients_dict))
        self.assertEqual(4, len(txm_event.active_donors_dict))
        self.assertEqual(3, res.json['recipients_uploaded'])
        self.assertEqual(4, res.json['donors_uploaded'])
        self.assertEqual(1, len(UploadedDataModel.query.all()))
        self.assertSetEqual({BloodGroup.ZERO, BloodGroup.A},
                            set(blood for blood in txm_event.active_recipients_dict[1].acceptable_blood_groups))
        self.assertEqual(HLATyping(hla_types_list=[HLAType('A1'), HLAType('A23'), HLAType('INVALID')]),
                         txm_event.active_donors_dict[1].parameters.hla_typing)
        self.assertSetEqual({'A1', 'A23'}, _get_hla_typing_codes(txm_event.active_donors_dict[1]))
        self.assertSetEqual({'A9'}, _get_hla_antibodies_codes(txm_event.active_recipients_dict[1]))
        self._check_expected_errors_in_db(2)

    def test_txm_event_patient_failed_upload_invalid_txm_event_name(self):
        txm_event_name = 'invalid_name'
        res, _ = self._txm_event_upload(donors_json=DONORS,
                                        recipients_json=RECIPIENTS,
                                        txm_event_name=txm_event_name)
        self._check_response(res, 400,
                             error_message=f'No TXM event with name "{txm_event_name}" found.')

    def test_txm_event_patient_failed_upload_invalid_waiting_since_date(self):

        res, _ = self._txm_event_upload(donors_json=DONORS,
                                        recipients_json=SPECIAL_RECIPIENTS_WAITING_SINCE_DATE_INVALID)
        self._check_response(res, 400,
                             error_message='Invalid date "2020-13-06". It must be in format "YYYY-MM-DD", e.g., '
                                           '"2020-12-31".')

    def test_txm_event_patient_failed_upload_invalid_recipient_donor_types(self):

        # Case 1 - recipient, DONOR type expected
        res, _ = self._txm_event_upload(donors_json=SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_EXISTING_RECIPIENT_ID,
                                        recipients_json=RECIPIENTS)
        self._check_response(res, 400,
                             error_message='When recipient is set, donor type must be "DONOR" but was NON_DIRECTED.')

        # Case 2 - None recipient, BRIDGING_DONOR or NON_DIRECTED type expected (related_recipient_medical_id not set)
        res, _ = self._txm_event_upload(donors_json=SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_MISSING_RECIPIENT_ID,
                                        recipients_json=RECIPIENTS)
        self._check_response(res, 400,
                             error_message='When recipient is not set, donor type must be "BRIDGING_DONOR" or'
                                           ' "NON_DIRECTED" but was "DONOR".')

    def test_txm_event_patient_failed_upload_invalid_related_medical_id_in_donor(self):
        res, _ = self._txm_event_upload(donors_json=SPECIAL_DONORS_INVALID_RECIPIENT_MEDICAL_ID,
                                        recipients_json=RECIPIENTS)
        self._check_response(res, 400,
                             error_message='Donor (medical id "D1") has related recipient (medical id "invalid_id"),'
                                           ' which was not found among recipients.')

    def test_txm_event_patient_failed_upload_duplicate_related_recipient_medical_id_in_donors(self):

        res, _ = self._txm_event_upload(donors_json=SPECIAL_DONORS_DUPLICATED_RECIPIENT_MEDICAL_IDS,
                                        recipients_json=RECIPIENTS)
        self._check_response(res, 400, error_message='Duplicate recipient medical ids found: [\'R1\'].')

    def test_txm_event_patient_successful_upload_special_hla_typing(self):
        res, txm_event = self._txm_event_upload(donors_json=SPECIAL_DONORS_SPECIAL_HLA_CODES,
                                                recipients_json=SPECIAL_RECIPIENTS_SPECIAL_HLA_CODES)

        self._check_response(res, 200)
        txm_event = get_txm_event(txm_event.db_id)
        recipient = txm_event.active_recipients_dict[1]
        expected_antibodies = {'DPA1', 'DP4', 'A23'}
        self.assertSetEqual(expected_antibodies, {hla_antibody.code for hla_antibody in
                                                  recipient.hla_antibodies.hla_antibodies_list})
        expected_typing = {'DQA1', 'A1', 'DQ6', 'B7'}
        self.assertSetEqual(expected_typing, _get_hla_typing_codes(recipient))
        donor = txm_event.active_donors_dict[1]
        expected_typing = {'B7', 'DQA1', 'DQ6'}
        self.assertSetEqual(expected_typing, _get_hla_typing_codes(donor))
        self._check_expected_errors_in_db(0)

    def test_txm_event_patient_successful_upload_multiple_same_hla_types(self):
        res, txm_event = self._txm_event_upload(donors_json=SPECIAL_DONORS_SPECIAL_HLA_CODES,
                                                recipients_json=SPECIAL_RECIPIENTS_MULTIPLE_SAME_HLA_CODES)

        self._check_response(res, 200)
        txm_event = get_txm_event(txm_event.db_id)
        recipient = txm_event.active_recipients_dict[1]
        expected_antibodies = {'DQA6', 'DQ8'}
        self.assertSetEqual(expected_antibodies, _get_hla_antibodies_codes(recipient))
        self._check_expected_errors_in_db(0)

    def test_txm_event_patient_successful_upload_exceptional_hla_types(self):
        res, txm_event = self._txm_event_upload(donors_json=SPECIAL_DONORS_SPECIAL_HLA_CODES,
                                                recipients_json=SPECIAL_RECIPIENTS_EXCEPTIONAL_HLA_CODES)
        self._check_response(res, 200)
        txm_event = get_txm_event(txm_event.db_id)
        recipient = txm_event.active_recipients_dict[1]
        expected_antibodies = {'DR9', 'CW6', 'B82', 'CW4'}
        self.assertSetEqual(expected_antibodies, _get_hla_antibodies_codes(recipient))

    def _txm_event_upload(self,
                          donors_json: Optional[List[Dict]] = None,
                          recipients_json: Optional[List[Dict]] = None,
                          country: str = Country.CZE.value,
                          txm_event_name: Optional[str] = None) -> Tuple[Response, TxmEvent]:
        if recipients_json is None:
            recipients_json = []
        if donors_json is None:
            donors_json = []
        self.fill_db_with_patients_and_results()
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)
        if not txm_event_name:
            txm_event_name = txm_event.name

        upload_patients = {
            'country': country,
            'txm_event_name': txm_event_name,
            'donors': donors_json,
            'recipients': recipients_json
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'{API_VERSION}/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )
            if res.status_code != 200:
                db.session.rollback()
            return res, txm_event

    def _check_response(self, res: Response,
                        status_code: int,
                        json_exists: bool = True,
                        error_message: Optional[str] = None):
        self.assertEqual(status_code, res.status_code)
        self.assertEqual('application/json', res.content_type)
        if json_exists:
            self.assertIsNotNone(res.json)
        if error_message:
            self.assertEqual(error_message, res.json['message'])

    def _check_expected_errors_in_db(self, expected_count: int):
        errors = ParsingErrorModel.query.all()
        self.assertEqual(expected_count, len(errors))


def _get_hla_typing_codes(donor_or_recipient: Patient) -> Set[str]:
    return {code for codes_per_group in
            donor_or_recipient.parameters.hla_typing.codes_per_group for code in
            codes_per_group.hla_codes}


def _get_hla_antibodies_codes(donor_or_recipient: Recipient) -> Set[str]:
    return {code for codes_per_group in
            donor_or_recipient.hla_antibodies.hla_codes_over_cutoff_per_group for code in
            codes_per_group.hla_codes}
