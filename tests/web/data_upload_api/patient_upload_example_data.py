TXM_EVENT_NAME = 'test'

VALID_UPLOAD_1 = {
    'donors': [
        {
            'sex': 'M',
            'donor_type': 'DONOR',
            'hla_typing': [
                'A2'
            ],
            'medical_id': 'TEST2',
            'blood_group': 'A',
            'year_of_birth': 1970,
            'waiting_since': '2015-01-17',
            'related_recipient_medical_id': 'TEST1'
        }
    ],
    'country': 'ISR',
    'recipients': [
        {
            'sex': 'M',
            'hla_typing': [
                'A1'
            ],
            'medical_id': 'TEST1',
            'blood_group': 0,
            'year_of_birth': 1945,
            'hla_antibodies': [
                {
                    'mfi': 2350,
                    'name': 'sdfsdfafaf',
                    'cutoff': 2000
                }
            ],
            'acceptable_blood_groups': [
                'A', 0
            ]
        }
    ],
    'txm_event_name': TXM_EVENT_NAME
}

VALID_UPLOAD_MISSING_FIELDS = {
    'donors': [
        {
            'sex': 'M',
            'donor_type': 'DONOR',
            'hla_typing': [
                'A2'
            ],
            'medical_id': 'TEST2',
            'blood_group': 'A',
            'related_recipient_medical_id': 'TEST1'
        }
    ],
    'country': 'ISR',
    'recipients': [
        {
            'hla_typing': [
                'A1'
            ],
            'medical_id': 'TEST1',
            'blood_group': 0,
            'hla_antibodies': [
                {
                    'mfi': 2350,
                    'name': 'sdfsdfafaf',
                    'cutoff': 2000
                }
            ]
        }
    ],
    'txm_event_name': TXM_EVENT_NAME
}

VALID_UPLOAD_SPECIAL_HLA_CODES = {
    'donors': [
        {
            'sex': 'M',
            'donor_type': 'DONOR',
            'hla_typing': [
                'DQ[01:03,      06:03]', 'B7'
            ],
            'medical_id': 'TEST2',
            'blood_group': 'A',
            'related_recipient_medical_id': 'TEST1'
        }
    ],
    'country': 'ISR',
    'recipients': [
        {
            'hla_typing': [
                'DQ[01:03,      06:03]', 'B7', 'A1'
            ],
            'medical_id': 'TEST1',
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
    ],
    'txm_event_name': TXM_EVENT_NAME
}
