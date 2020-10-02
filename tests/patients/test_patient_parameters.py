from txmatching.patients.patient_parameters import (HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.utils.enums import Country

donor_parameters_Joe = PatientParameters(
    blood_group='A',
    country_code=Country.CZE,
    hla_typing=HLATyping(
        [HLAType('A11'),
         HLAType('A26'),
         HLAType('B38'),
         HLAType('B62'),
         HLAType('DR4'),
         HLAType('DR11'),
         HLAType('DR52'),
         HLAType('DR53'),
         HLAType('DQ7'),
         HLAType('DQ8'),
         HLAType('DP2'),
         HLAType('DP10'),
         HLAType('CW9'),
         HLAType('CW12')
         ]
    )
)

recipient_parameters_Jack = PatientParameters(blood_group='A',
                                              hla_typing=HLATyping(
                                                  [
                                                      HLAType('A1'),
                                                      HLAType('A30'),
                                                      HLAType('B14'),
                                                      HLAType('B15'),
                                                      HLAType('B62'),
                                                      HLAType('B63'),
                                                      HLAType('B64'),
                                                      HLAType('B65'),
                                                      HLAType('B75'),
                                                      HLAType('B76'),
                                                      HLAType('B77'),
                                                      HLAType('DR4'),
                                                      HLAType('DR11')
                                                  ]
                                              ),
                                              country_code=Country.CZE
                                              )
