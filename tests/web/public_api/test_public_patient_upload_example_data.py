from txmatching.patients.patient import DonorType
from txmatching.utils.enums import Sex

DONORS = [
    {
        'medical_id': 'D1',
        'internal_medical_id': 'TEST_INTERNAL_MEDICAL_ID',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23', 'Invalid', 'B*01:01N', 'BW4'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965
    },
    {
        'medical_id': 'D2',
        'blood_group': 'B',
        'hla_typing': [
            'A1', 'A23'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R2',
        'sex': Sex.M,
        'height': 178,
        'weight': 69,
        'year_of_birth': 1967
    },
    {
        # Missing related_recipient_medical_id and also all non required fields
        'medical_id': 'donor_missing_non_required_fields',
        'blood_group': '0',
        'hla_typing': [],
        'donor_type': DonorType.NON_DIRECTED.value,
    },
    {
        'medical_id': 'D4',
        'blood_group': 'AB',
        'hla_typing': [
            'A1'
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
            'A1', 'A23'
        ],
        'hla_antibodies': [
            {
                'mfi': 2350,
                'name': 'sdfsdfafaf',
                'cutoff': 2000
            },
            {
                'mfi': 2350,
                'name': 'A9',
                'cutoff': 2000
            }
        ],
        'sex': Sex.F,
        'height': 150,
        'weight': 65,
        'year_of_birth': 2001,
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
            'A1', 'A23'
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
        'previous_transplants': 0
    },
    # missing non required fields
    {
        'medical_id': 'recipient_missing_non_required_fields',
        'blood_group': '0',
        'hla_typing': [],
        'hla_antibodies': []
    }
]

SPECIAL_DONORS_DUPLICATED_RECIPIENT_MEDICAL_IDS = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965
    },
    {
        'medical_id': 'D2',
        'blood_group': 'A',
        'hla_typing': [
            'A1'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.F,
        'height': 187,
        'weight': 97,
        'year_of_birth': 1969
    }
]

SPECIAL_DONORS_INVALID_RECIPIENT_MEDICAL_ID = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23'
        ],
        'donor_type': DonorType.DONOR.value,
        'related_recipient_medical_id': 'invalid_id',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965
    }
]

SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_MISSING_RECIPIENT_ID = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23'
        ],
        'donor_type': DonorType.DONOR.value,
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965
    }
]

SPECIAL_DONORS_DONOR_TYPE_NOT_COMPATIBLE_WITH_EXISTING_RECIPIENT_ID = [
    {
        'medical_id': 'D1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23'
        ],
        'donor_type': DonorType.NON_DIRECTED.value,
        'related_recipient_medical_id': 'R1',
        'sex': Sex.M,
        'height': 180,
        'weight': 90,
        'year_of_birth': 1965
    }
]

SPECIAL_RECIPIENTS_WAITING_SINCE_DATE_INVALID = [
    {
        'acceptable_blood_groups': [
            'A',
            '0'
        ],
        'medical_id': 'R1',
        'blood_group': 'A',
        'hla_typing': [
            'A1', 'A23'
        ],
        'hla_antibodies': [
            {
                'name': 'B42',
                'mfi': 2000,
                'cutoff': 2100
            }
        ],
        'sex': Sex.F,
        'height': 150,
        'weight': 65,
        'year_of_birth': 21,
        'waiting_since': '2020-13-06',
        'previous_transplants': 0
    }
]

SPECIAL_DONORS_SPECIAL_HLA_CODES = [
    {
        'sex': 'M',
        'donor_type': 'DONOR',
        'hla_typing': [
            'DQ[01:03,      06:03]', 'B7'
        ],
        'medical_id': 'R1',
        'blood_group': 'A',
        'related_recipient_medical_id': 'R1'
    }
]

SPECIAL_RECIPIENTS_SPECIAL_HLA_CODES = [
    {
        'hla_typing': [
            'DQ[01:03,      06:03]', 'B7', 'A1'
        ],
        'medical_id': 'R1',
        'blood_group': 0,
        'hla_antibodies': [
            {
                'mfi': 2350,
                'name': 'DP4 [01:03, 04:02]',
                'cutoff': 2000
            },
            {
                'mfi': 200,
                'name': 'A23',
                'cutoff': 2000
            }
        ]
    }
]

SPECIAL_RECIPIENTS_MULTIPLE_SAME_HLA_CODES = [
    {
        'hla_typing': [
            'DQ[01:03,      06:03]', 'B7', 'A1'
        ],
        'medical_id': 'R1',
        'blood_group': 0,
        'hla_antibodies': [
            {
                'mfi': 222,
                'name': 'DQ[05:01,02:01]',
                'cutoff': 4000
            },
            {
                'mfi': 87,
                'name': 'DQ[05:01,02:02]',
                'cutoff': 4000
            },
            {
                'mfi': 87,
                'name': 'DQ[05:01,02:02]',
                'cutoff': 4000
            },
            {
                'mfi': 3900,
                'name': 'DQ[06:01,03:01]',
                'cutoff': 4000
            },
            {
                'mfi': 4200,
                'name': 'DQ[06:01,03:02]',
                'cutoff': 4000
            },
            {
                'mfi': 4200,
                'name': 'DQ[06:02,03:02]',
                'cutoff': 4000},
        ]
    }
]

SPECIAL_RECIPIENTS_EXCEPTIONAL_HLA_CODES = [
    {
        'sex': 'M',
        'hla_typing': [
            'A1'
        ],
        'medical_id': 'R1',
        'blood_group': 0,
        'year_of_birth': 1945,
        'hla_antibodies': [
            {
                'mfi': 2350,
                'name': 'B*82:02',
                'cutoff': 2000
            },
            {
                'mfi': 2350,
                'name': 'DRB1*09:02',
                'cutoff': 2000
            },
            {
                'mfi': 2350,
                'name': 'C*04:03',
                'cutoff': 2000
            }
        ],
        'acceptable_blood_groups': [
            'A', 0
        ]
    }
]
