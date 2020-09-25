from txmatching.patients.patient_parameters import HLATyping, PatientParameters
from txmatching.utils.enums import Country

donor_parameters_Joe = PatientParameters(
    blood_group='A',
    country_code=Country.CZE,
    hla_typing=HLATyping(
        ['A11',
         'A26',
         'B38',
         'B62',
         'DR4',
         'DR11',
         'DR52',
         'DR53',
         'DQ7',
         'DQ8',
         'DP2',
         'DP10',
         'Cw9',
         'Cw12'
         ]
    )
)

recipient_parameters_Jack = PatientParameters(blood_group='A',
                                              hla_typing=HLATyping(
                                                  [
                                                      'A1',
                                                      'A30',
                                                      'B14',
                                                      'B15',
                                                      'B62',
                                                      'B63',
                                                      'B64',
                                                      'B65',
                                                      'B75',
                                                      'B76',
                                                      'B77',
                                                      'DR4',
                                                      'DR11'
                                                  ]
                                              ),
                                              country_code=Country.CZE
                                              )
