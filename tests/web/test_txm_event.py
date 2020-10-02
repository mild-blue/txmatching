from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.data_types import UserRole
from txmatching.database.db import db
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.services.txm_event_service import (
    create_txm_event, get_newest_txm_event_db_id)
from txmatching.database.sql_alchemy_schema import (ConfigModel, DonorModel,
                                                    PairingResultModel,
                                                    RecipientModel)
from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Country, Sex
from txmatching.web import (REPORTS_NAMESPACE, TXM_EVENT_NAMESPACE, report_api,
                            txm_event_api)

DONORS = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'HLA_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'YOB': 1965
    },
    {
        'medical_id': 'D2',
        'blood_group': 'B',
        'HLA_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R2',
        'sex': Sex.M,
        'height': 178,
        'weight': 69,
        'YOB': 1967
    },
    {
        # Missing related_recipient_medical_id
        'medical_id': 'D3',
        'blood_group': '0',
        'HLA_typing': [
            'A9', 'A21'
        ],
        'donor_type': DonorType.NON_DIRECTED.value,
        'sex': Sex.M,
        'height': 146,
        'weight': 89,
        'YOB': 1960
    },
    {
        'medical_id': 'D4',
        'blood_group': 'AB',
        'HLA_typing': [
            'A9'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R3',
        'sex': Sex.M,
        'height': 145,
        'weight': 56,
        'YOB': 1989
    },
]

RECIPIENTS = [
    {
        'acceptable_blood_groups': [
            'A',
            '0'
        ],
        'medical_id': 'R1',
        'blood_group': 'A',
        'HLA_typing': [
            'A9', 'A21'
        ],
        'HLA_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2100
            }
        ],
        'sex': Sex.F,
        'height': 150,
        'weight': 65,
        'YOB': 2001,
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
        'HLA_typing': [
            'A9', 'A21'
        ],
        'HLA_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2200
            }
        ],
        'sex': Sex.F,
        'height': 189,
        'weight': 70,
        'YOB': 1996,
        'waiting_since': '2020-02-07',
        'previous_transplants': 0
    },
    {
        'acceptable_blood_groups': [
            '0'
        ],
        'medical_id': 'R3',
        'blood_group': '0',
        'HLA_typing': [
            'A9', 'A21'
        ],
        'HLA_antibodies': [
            {
                'name': 'B43',
                'mfi': 2000,
                'cutoff': 2300
            }
        ],
        'sex': Sex.M,
        'height': 201,
        'weight': 120,
        'YOB': 1999,
        'waiting_since': '2020-05-13',
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
        self.assertEqual(1, len(configs))
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
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)

        txm_name = 'test'

        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': txm_name,
            'donors': DONORS,
            'recipients': RECIPIENTS
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            self.assertEqual(200, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertIsNotNone(res.json)

        self.assertEqual(txm_name, txm_event.name)
        self.assertEqual(3, len(RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(4, len(DonorModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(3, res.json['recipients_uploaded'])
        self.assertEqual(4, res.json['donors_uploaded'])

    def test_txm_event_patient_failed_upload_invalid_txm_event_name(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')

        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': 'invalid_name',
            'donors': DONORS,
            'recipients': RECIPIENTS
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('No TXM event with name "invalid_name" found.', res.json['message'])

    def test_txm_event_patient_failed_upload_invalid_waiting_since_date(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')

        txm_name = 'test'

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
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'HLA_antibodies': [
                        {
                            'name': 'B43',
                            'mfi': 2000,
                            'cutoff': 2100
                        }
                    ],
                    'sex': Sex.F,
                    'height': 150,
                    'weight': 65,
                    'YOB': 21,
                    'waiting_since': '2020-13-06',
                    'previous_transplants': 0
                }
            ]
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('Invalid date "2020-13-06". It must be in format "YYYY-MM-DD", e.g., "2020-12-31".',
                             res.json['message'])

    def test_txm_event_patient_failed_upload_invalid_recipient_donor_types(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')

        txm_name = 'test'

        # Case 1 - recipient, DONOR type expected
        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': txm_name,
            'donors': [
                {
                    'medical_id': 'D1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'donor_type': DonorType.NON_DIRECTED.value,
                    'related_recipient_medical_id': 'R1',
                    'sex': Sex.M,
                    'height': 180,
                    'weight': 90,
                    'YOB': 1965
                }
            ],
            'recipients': [
                {
                    'acceptable_blood_groups': [
                        'A',
                        '0'
                    ],
                    'medical_id': 'R1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'HLA_antibodies': [
                        {
                            'name': 'B43',
                            'mfi': 2000,
                            'cutoff': 2100
                        }
                    ],
                    'sex': Sex.F,
                    'height': 150,
                    'weight': 65,
                    'YOB': 2001,
                    'waiting_since': '2020-01-06',
                    'previous_transplants': 0
                }
            ]
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('When recipient is set, donor type must be "DONOR".', res.json['message'])

        # Case 2 - None recipient, BRIDGING_DONOR or NON_DIRECTED type expected (related_recipient_medical_id is not set)
        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': txm_name,
            'donors': [
                {
                    'medical_id': 'D1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'donor_type': DonorType.DONOR.value,
                    'sex': Sex.M,
                    'height': 180,
                    'weight': 90,
                    'YOB': 1965
                }
            ],
            'recipients': [
                {
                    'acceptable_blood_groups': [
                        'A',
                        '0'
                    ],
                    'medical_id': 'R2',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'HLA_antibodies': [
                        {
                            'name': 'B43',
                            'mfi': 2000,
                            'cutoff': 2100
                        }
                    ],
                    'sex': Sex.F,
                    'height': 150,
                    'weight': 65,
                    'YOB': 2001,
                    'waiting_since': '2020-01-06',
                    'previous_transplants': 0
                }
            ]
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual(
                'When recipient is not set, donor type must be "BRIDGING_DONOR" or "NON_DIRECTED".',
                res.json['message']
            )

    def test_txm_event_patient_failed_upload_invalid_related_medical_id_in_donor(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')

        txm_name = 'test'

        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': txm_name,
            'donors': [
                {
                    'medical_id': 'D1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'donor_type': DonorType.DONOR.value,
                    'related_recipient_medical_id': 'R1',
                    'sex': Sex.M,
                    'height': 180,
                    'weight': 90,
                    'YOB': 1965
                }
            ],
            'recipients': [
                {
                    'acceptable_blood_groups': [
                        'A',
                        '0'
                    ],
                    'medical_id': 'R2',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'HLA_antibodies': [
                        {
                            'name': 'B43',
                            'mfi': 2000,
                            'cutoff': 2100
                        }
                    ],
                    'sex': Sex.F,
                    'height': 150,
                    'weight': 65,
                    'YOB': 2001,
                    'waiting_since': '2020-01-06',
                    'previous_transplants': 0
                }
            ]
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('When recipient is not set, donor type must be "BRIDGING_DONOR" or "NON_DIRECTED".',
                             res.json['message'])

    def test_txm_event_patient_failed_upload_duplicate_related_recipient_medical_id_in_donors(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')

        txm_name = 'test'

        upload_patients = {
            'country': Country.CZE.value,
            'txm_event_name': txm_name,
            'donors': [
                {
                    'medical_id': 'D1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'donor_type': DonorType.DONOR.value,
                    'related_recipient_medical_id': 'R1',
                    'sex': Sex.M,
                    'height': 180,
                    'weight': 90,
                    'YOB': 1965
                },
                {
                    'medical_id': 'D2',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9'
                    ],
                    'donor_type': DonorType.DONOR.value,
                    'related_recipient_medical_id': 'R1',
                    'sex': Sex.F,
                    'height': 187,
                    'weight': 97,
                    'YOB': 1969
                }
            ],
            'recipients': [
                {
                    'acceptable_blood_groups': [
                        'A',
                        '0'
                    ],
                    'medical_id': 'R1',
                    'blood_group': 'A',
                    'HLA_typing': [
                        'A9', 'A21'
                    ],
                    'HLA_antibodies': [
                        {
                            'name': 'B43',
                            'mfi': 2000,
                            'cutoff': 2100
                        }
                    ],
                    'sex': Sex.F,
                    'height': 150,
                    'weight': 65,
                    'YOB': 2001,
                    'waiting_since': '2020-01-06',
                    'previous_transplants': 0
                }
            ]
        }

        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            res = client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=upload_patients
            )

            db.session.rollback()

            self.assertEqual(400, res.status_code)
            self.assertEqual('application/json', res.content_type)
            self.assertEqual('Duplicate recipient medical ids found: [\'R1\'].', res.json['message'])
