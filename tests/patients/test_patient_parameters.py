from txmatching.patients.patient_parameters import (HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.utils.enums import Country

donor_parameters_Joe = PatientParameters(
    blood_group='A',
    country_code=Country.CZE,
    hla_typing=HLATyping(
        [HLAType('A11', 'A11'),
         HLAType('A26', 'A26'),
         HLAType('B38', 'B38'),
         HLAType('B62', 'B62'),
         HLAType('DR4', 'DR4'),
         HLAType('DR11', 'DR11'),
         HLAType('DR52', 'DR52'),
         HLAType('DR53', 'DR53'),
         HLAType('DQ7', 'DQ7'),
         HLAType('DQ8', 'DQ8'),
         HLAType('DP2', 'DP2'),
         HLAType('DP10', 'DP10'),
         HLAType('Cw9', 'Cw9'),
         HLAType('Cw12', 'Cw12')
         ]
    )
)

recipient_parameters_Jack = PatientParameters(blood_group='A',
                                              hla_typing=HLATyping(
                                                  [
                                                      HLAType('A1', 'A1'),
                                                      HLAType('A30', 'A30'),
                                                      HLAType('B14', 'B14'),
                                                      HLAType('B15', 'B15'),
                                                      HLAType('B62', 'B62'),
                                                      HLAType('B63', 'B63'),
                                                      HLAType('B64', 'B64'),
                                                      HLAType('B65', 'B65'),
                                                      HLAType('B75', 'B75'),
                                                      HLAType('B76', 'B76'),
                                                      HLAType('B77', 'B77'),
                                                      HLAType('DR4', 'DR4'),
                                                      HLAType('DR11', 'DR11')
                                                  ]
                                              ),
                                              country_code=Country.CZE
                                              )
