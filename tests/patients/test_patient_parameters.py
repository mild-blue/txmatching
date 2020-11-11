from txmatching.patients.patient_parameters import (HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country

donor_parameters_Joe = PatientParameters(
    blood_group=BloodGroup.A,
    country_code=Country.CZE,
    hla_typing=HLATyping(
        [HLAType('A23'),
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

recipient_parameters_Jack = PatientParameters(blood_group=BloodGroup.A,
                                              hla_typing=HLATyping(
                                                  [
                                                      HLAType('A9'),
                                                      HLAType('A30'),
                                                      HLAType('B14'),
                                                      HLAType('B77'),
                                                      HLAType('DR4'),
                                                      HLAType('DR11')
                                                  ]
                                              ),
                                              country_code=Country.CZE
                                              )
