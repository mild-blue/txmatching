from txmatching.patients.hla_model import (HLAAntibodies, HLAAntibody, HLAType,
                                           HLATyping)
from txmatching.patients.patient import (Donor, DonorType, Recipient,
                                         RecipientRequirements)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Sex

_RAW_CODES = [
    'A1',
    'A32',
    'B7',
    'B51',
    'DR11',
    'DR15'
]


def get_test_raw_codes():
    return _RAW_CODES.copy()


def get_test_donors():
    return [
        Donor(
            db_id=1,
            medical_id='1',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    hla_types_list=[
                        HLAType(raw_code=_RAW_CODES[0]),
                        HLAType(raw_code=_RAW_CODES[1]),
                        HLAType(raw_code='B44'),
                        HLAType(raw_code='DR10')
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985
            ),
            related_recipient_db_id=None,
            donor_type=DonorType.DONOR
        ),
        Donor(
            db_id=2,
            medical_id='2',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    hla_types_list=[
                        HLAType(raw_code=_RAW_CODES[1]),
                        HLAType(raw_code=_RAW_CODES[2]),
                        HLAType(raw_code='DR10')
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985
            ),
            related_recipient_db_id=None,
            donor_type=DonorType.DONOR
        )
    ]


def get_test_recipients():
    return [
        Recipient(
            db_id=3,
            medical_id='3',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    hla_types_list=[
                        HLAType(raw_code=_RAW_CODES[1]),
                        HLAType(raw_code=_RAW_CODES[2]),
                        HLAType(raw_code='DR1')
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985
            ),
            related_donor_db_id=1,
            acceptable_blood_groups=[],
            recipient_cutoff=None,
            hla_antibodies=HLAAntibodies([]),
            recipient_requirements=RecipientRequirements(),
            waiting_since=None,
            previous_transplants=None
        ),
        Recipient(
            db_id=4,
            medical_id='4',
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=HLATyping(
                    hla_types_list=[
                        HLAType(raw_code='A3'),
                        HLAType(raw_code='B38'),
                        HLAType(raw_code=_RAW_CODES[4]),
                        HLAType(raw_code=_RAW_CODES[5]),
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985
            ),
            related_donor_db_id=1,
            acceptable_blood_groups=[],
            recipient_cutoff=None,
            hla_antibodies=HLAAntibodies([]),
            recipient_requirements=RecipientRequirements(),
            waiting_since=None,
            previous_transplants=None
        ),
    ]


def get_test_antibodies():
    return HLAAntibodies(
        hla_antibodies_list=[
            HLAAntibody('A7', 1200, 1000, 'A7'),
            HLAAntibody('B32', 1200, 1000, 'B32'),
            HLAAntibody('DR40', 1200, 1000, 'DR40'),
            HLAAntibody('B5', 1200, 1000, 'B5'),
            HLAAntibody('DR9', 1200, 1000, 'DR9'),
            HLAAntibody('A23', 1200, 1000, 'A23')
        ]
    )
