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
                },
                {
                    'mfi': 2350,
                    'name': 'A9',
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

VALID_UPLOAD_MULTIPLE_SAME_HLA_CODES = {
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
    ],
    'txm_event_name': TXM_EVENT_NAME
}

VALID_UPLOAD_EXCEPTIONAL_CODES = {
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
    ],
    'txm_event_name': TXM_EVENT_NAME
}
