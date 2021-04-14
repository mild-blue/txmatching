from tests.test_utilities.hla_preparation_utils import create_hla_typing
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country

joe_hla_typing = ['A23',
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
                  'CW9',
                  'CW12'
                  ]
donor_parameters_Joe = PatientParameters(
    blood_group=BloodGroup.A,
    country_code=Country.CZE,
    hla_typing=create_hla_typing(joe_hla_typing)
)

jack_hla_typing = ['A9',
                   'A30',
                   'B14',
                   'B77',
                   'DR4',
                   'DR11'
                   ]

recipient_parameters_Jack = PatientParameters(blood_group=BloodGroup.A,
                                              hla_typing=create_hla_typing(jack_hla_typing),
                                              country_code=Country.CZE
                                              )

recipient_parameters_Wrong = PatientParameters(blood_group=BloodGroup.A,
                                               hla_typing=create_hla_typing(
                                                   [
                                                       'A9',
                                                       'A30',
                                                       'A31',
                                                       'B14',
                                                       'B77',
                                                       'DR4',
                                                       'DR11'
                                                   ]
                                               ),
                                               country_code=Country.CZE
                                               )
