from txmatching.database.db import db
from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.services.txm_event_service import create_txm_event, \
    get_newest_txm_event_db_id
from txmatching.database.sql_alchemy_schema import ConfigModel, RecipientModel, PairingResultModel, DonorModel
from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Country
from txmatching.web import report_api, REPORTS_NAMESPACE, txm_event_api, TXM_EVENT_NAMESPACE

DONORS = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'hla_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': 'M',
        'height': 180,
        'weight': 90,
        'yob': 33
    },
    {
        'medical_id': 'D2',
        'blood_group': 'B',
        'hla_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.BRIDGING_DONOR.value,
        'related_recipient_medical_id': 'R3',
        'sex': 'M',
        'height': 178,
        'weight': 69,
        'yob': 45
    },
    {
        'medical_id': 'D3',
        'blood_group': '0',
        'hla_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': 'M',
        'height': 146,
        'weight': 89,
        'yob': 50
    }
]

RECIPIENTS = [
    {
        'acceptable_blood_groups': [
            'A',
            '0'
        ],
        'medical_id': 'R1',
        'blood_group': 'A',
        'hla_typing': [
            'A9', 'A21'
        ],
        'hla_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2100
            }
        ],
        'sex': 'F',
        'height': 150,
        'weight': 65,
        'yob': 21,
        'waiting_since': '2020-01-06',
        'previous_transplants': 0
    },
    {
        'acceptable_blood_groups': [
            'B',
            '0'
        ],
        'medical_id': 'R2',
        'blood_group': 'B',
        'hla_typing': [
            'A9', 'A21'
        ],
        'hla_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2200
            }
        ],
        'sex': 'F',
        'height': 189,
        'weight': 70,
        'yob': 65,
        'waiting_since': '2020-02-07',
        'previous_transplants': 0
    },
    {
        'acceptable_blood_groups': [
            '0'
        ],
        'medical_id': 'R3',
        'blood_group': '0',
        'hla_typing': [
            'A9', 'A21'
        ],
        'hla_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2300
            }
        ],
        'sex': 'F',
        'height': 201,
        'weight': 120,
        'yob': 14,
        'waiting_since': '2020-05-13',
        'previous_transplants': 0
    },
    {
        'acceptable_blood_groups': [
            '0'
        ],
        'medical_id': 'R4',
        'blood_group': 'AB',
        'hla_typing': [
            'A9', 'A21'
        ],
        'hla_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2400
            }
        ],
        'sex': 'M',
        'height': 196,
        'weight': 80,
        'yob': 63,
        'waiting_since': '2020-04-19',
        'previous_transplants': 0
    }
]


class TestMatchingApi(DbTests):

    def test_txm_event_creation_and_deletion(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(2, len(txm_event.donors_dict))
        self.assertEqual(2, len(configs))
        self.assertEqual(1, len(PairingResultModel.query.filter(PairingResultModel.config_id.in_(
            [config.id for config in configs])).all()))

        txm_name = 'test'

        with self.assertRaises(ValueError):
            create_txm_event(txm_name)
        txm_event = create_or_overwrite_txm_event(txm_name)
        self.assertEqual(txm_name, txm_event.name)
        self.assertEqual(0, len(RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(0, len(ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()))

    def test_txm_event_patient_successful_upload(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)

        txm_name = 'test'

        with self.app.test_client() as client:
            upload_patients = {
                'country': Country.CZE.value,
                'txm_event_name': txm_name,
                'donors': DONORS,
                'recipients': RECIPIENTS
            }

            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual("application/json", res.content_type)
            self.assertIsNotNone(res.json)

        self.assertEqual(txm_name, txm_event.name)
        self.assertEqual(4, len(RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(3, len(DonorModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(4, res.json['recipients_uploaded'])
        self.assertEqual(3, res.json['donors_uploaded'])

    def test_txm_event_patient_failed_upload_invalid_txm_event_name(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)

        with self.app.test_client() as client:
            upload_patients = {
                'country': Country.CZE.value,
                'txm_event_name': 'invalid_name',
                'donors': DONORS,
                'recipients': RECIPIENTS
            }

            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(500, res.status_code)  # TODO: Fix to check error 400/404
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('Internal Server Error', res.json['message'])

    def test_txm_event_patient_failed_upload_invalid_waiting_since_date(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)

        txm_name = 'test'

        with self.app.test_client() as client:
            upload_patients = {
                'country': Country.CZE.value,
                'txm_event_name': txm_name,
                'donors': DONORS,
                'recipients': [
                    {
                        'acceptable_blood_groups': [
                            'A',
                            '0'
                        ],
                        'medical_id': 'R1',
                        'blood_group': 'A',
                        'hla_typing': [
                            'A9', 'A21'
                        ],
                        'hla_antibodies': [
                            {
                                'name': 'B43',
                                'mfi': 2000,
                                'cutoff': 2100
                            }
                        ],
                        'sex': 'F',
                        'height': 150,
                        'weight': 65,
                        'yob': 21,
                        'waiting_since': '2020-13-06',
                        'previous_transplants': 0
                    }
                ]
            }

            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(500, res.status_code)  # TODO: Fix to check error 400/404
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('Internal Server Error', res.json['message'])
