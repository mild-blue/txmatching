from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Sex

DONORS = [
    {
        'medical_id': 'D1',
        'internal_medical_id': 'TEST_INTERNAL_MEDICAL_ID',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23', 'B*07:02', 'BW4', 'DR3'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965,
        'note': 'donor note 1'
    },
    {
        'medical_id': 'D2',
        'blood_group': 'B',
        'hla_typing': [
            'A1', 'A23', 'B7', 'DR3'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R2',
        'sex': Sex.M,
        'height': 178,
        'weight': 69,
        'year_of_birth': 1967,
        'note': 'donor note 2'
    },
    {
        # Missing related_recipient_medical_id and also all non required fields
        'medical_id': 'donor_missing_non_required_fields',
        'blood_group': '0',
        'hla_typing': ['A1', 'B7', 'DR3'],
        'donor_type': DonorType.NON_DIRECTED.value,
    },
    {
        'medical_id': 'D4',
        'blood_group': 'AB',
        'hla_typing': [
            'A1', 'B7', 'DR3'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'recipient_missing_non_required_fields',
        'sex': Sex.M,
        'height': 145,
        'weight': 56,
        'year_of_birth': 1989
    },
]

RECIPIENTS = [
    {
        'acceptable_blood_groups': [
            'A', '0'
        ],
        'medical_id': 'R1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23', 'B7', 'DR3'
        ],
        'hla_antibodies': [
            {
                'mfi': 2350,
                'name': 'A9',
                'cutoff': 2000
            },
            {
                'mfi': 100,
                'name': 'A9',
                'cutoff': 2000
            }
        ],
        'sex': Sex.F,
        'height': 150,
        'weight': 65,
        'year_of_birth': 2001,
        'waiting_since': '2020-01-06',
        'previous_transplants': 0,
        'note': 'recipient note 1'
    },
    {
        'acceptable_blood_groups': [
            'B',
            '0'
        ],
        'medical_id': 'R2',
        'blood_group': 'B',
        'hla_typing': [
            'A1', 'A23', 'B7', 'DR3'
        ],
        'hla_antibodies': [
            {
                'name': 'B42',
                'mfi': 2000,
                'cutoff': 2200
            }
        ],
        'sex': Sex.F,
        'height': 189,
        'weight': 70,
        'year_of_birth': 1996,
        'waiting_since': '2020-02-07',
        'previous_transplants': 0,
        'note': 'recipient note 2'
    },
    # missing non required fields
    {
        'medical_id': 'recipient_missing_non_required_fields',
        'blood_group': '0',
        'hla_typing': ['A3', 'B7', 'DR3'],
        'hla_antibodies': []
    }
]
