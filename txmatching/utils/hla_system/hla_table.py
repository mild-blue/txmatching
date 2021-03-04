from txmatching.utils.hla_system.rel_dna_ser_parsing import \
    SEROLOGICAL_CODES_IN_REL_DNA_SER

# the dict below is based on http://hla.alleles.org/antigens/recognised_serology.html

SPLIT_TO_BROAD = {'A23': 'A9',
                  'A24': 'A9',
                  'A25': 'A10',
                  'A26': 'A10',
                  'A29': 'A19',
                  'A30': 'A19',
                  'A31': 'A19',
                  'A32': 'A19',
                  'A33': 'A19',
                  'A34': 'A10',
                  'A66': 'A10',
                  'A68': 'A28',
                  'A69': 'A28',
                  'A74': 'A19',
                  'B38': 'B16',
                  'B39': 'B16',
                  'B44': 'B12',
                  'B45': 'B12',
                  'B49': 'B21',
                  'B50': 'B21',
                  'B51': 'B5',
                  'B52': 'B5',
                  'B54': 'B22',
                  'B55': 'B22',
                  'B56': 'B22',
                  'B57': 'B17',
                  'B58': 'B17',
                  'B60': 'B40',
                  'B61': 'B40',
                  'B62': 'B15',
                  'B63': 'B15',
                  'B64': 'B14',
                  'B65': 'B14',
                  'B71': 'B70',
                  'B72': 'B70',
                  'B75': 'B15',
                  'B76': 'B15',
                  'B77': 'B15',
                  'CW9': 'CW3',
                  'CW10': 'CW3',
                  'DR11': 'DR5',
                  'DR12': 'DR5',
                  'DR13': 'DR6',
                  'DR14': 'DR6',
                  'DR15': 'DR2',
                  'DR16': 'DR2',
                  'DR17': 'DR3',
                  'DR18': 'DR3',
                  'DQ5': 'DQ1',
                  'DQ6': 'DQ1',
                  'DQ7': 'DQ3',
                  'DQ8': 'DQ3',
                  'DQ9': 'DQ3'
                  }

BROAD_CODES = {SPLIT_TO_BROAD.get(hla_code, hla_code) for hla_code in SEROLOGICAL_CODES_IN_REL_DNA_SER}

SPLIT_CODES = SEROLOGICAL_CODES_IN_REL_DNA_SER

ALL_SPLIT_BROAD_CODES = SEROLOGICAL_CODES_IN_REL_DNA_SER.union(BROAD_CODES)
