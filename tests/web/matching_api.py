import unittest

from kidney_exchange.config.configuration import Configuration
from kidney_exchange.data_transfer_objects.configuration.configuration_to_dto import \
    configuration_to_dto
from kidney_exchange.web import create_app, API_VERSION, MATCHING_NAMESPACE, PATIENT_NAMESPACE


class TestSaveAndGetConfiguration(unittest.TestCase):
    def test_get_matchings(self):
        app = create_app()
        with app.test_client() as client:
            with app.app_context():
                conf_dto = configuration_to_dto(Configuration(
                    enforce_compatible_blood_group=False,
                    require_new_donor_having_better_match_in_compatibility_index=False,
                    require_new_donor_having_better_match_in_compatibility_index_or_blood_group=False))

                res = client.post(f'/{API_VERSION}/{MATCHING_NAMESPACE}/calculate-for-config', json=conf_dto)
                expected = [{'score': 36.0, 'rounds': [{'transplants': [
                    {'score': 18.0, 'compatible_blood': True, 'donor': 'P21', 'recipient': 'P12'},
                    {'score': 18.0, 'compatible_blood': True, 'donor': 'P22', 'recipient': 'P11'}]}],
                             'countries': [{'country_code': 'CZE', 'donor_count': 2, 'recipient_count': 2}]}]
                self.assertEqual(expected, res.json)

    def test_get_patients(self):
        app = create_app()
        with app.test_client() as client:
            res = client.get(f'/{API_VERSION}/{PATIENT_NAMESPACE}/')
            expected = [{'db_id': 1, 'medical_id': 'P21',
                         'parameters': {'blood_group': 'A', 'acceptable_blood_groups': [],
                                        'hla_antigens': {'codes': ['A11', 'B8', 'DR11']},
                                        'hla_antibodies': {'codes': []}, 'country_code': 'CZE'},
                         'patient_type': 'DONOR'}, {'db_id': 2, 'medical_id': 'P22',
                                                    'parameters': {'blood_group': '0', 'acceptable_blood_groups': [],
                                                                   'hla_antigens': {'codes': ['A2', 'B8', 'DR11']},
                                                                   'hla_antibodies': {'codes': []},
                                                                   'country_code': 'CZE'}, 'patient_type': 'DONOR'},
                        {'db_id': 3, 'medical_id': 'P11',
                         'parameters': {'blood_group': '0', 'acceptable_blood_groups': ['A', '0'],
                                        'hla_antigens': {'codes': ['A3', 'B7', 'DR11']},
                                        'hla_antibodies': {'codes': ['B7', 'DQ6', 'DQ5']}, 'country_code': 'CZE'},
                         'related_donor': {'db_id': 1, 'medical_id': 'P21',
                                           'parameters': {'blood_group': 'A', 'acceptable_blood_groups': [],
                                                          'hla_antigens': {'codes': ['A11', 'B8', 'DR11']},
                                                          'hla_antibodies': {'codes': []}, 'country_code': 'CZE'},
                                           'patient_type': 'DONOR'}, 'patient_type': 'RECIPIENT'},
                        {'db_id': 4, 'medical_id': 'P12',
                         'parameters': {'blood_group': 'A', 'acceptable_blood_groups': ['A', '0'],
                                        'hla_antigens': {'codes': ['A3', 'B7', 'DR11']},
                                        'hla_antibodies': {'codes': ['B7', 'DQ6', 'DQ5']}, 'country_code': 'CZE'},
                         'related_donor': {'db_id': 2, 'medical_id': 'P22',
                                           'parameters': {'blood_group': '0', 'acceptable_blood_groups': [],
                                                          'hla_antigens': {'codes': ['A2', 'B8', 'DR11']},
                                                          'hla_antibodies': {'codes': []}, 'country_code': 'CZE'},
                                           'patient_type': 'DONOR'}, 'patient_type': 'RECIPIENT'}]
            self.assertEqual(expected, res.json)
