from txmatching.patients.hla_model import HLAAntibodies, HLAType, HLATyping
from txmatching.patients.patient import (Donor, DonorType, Recipient,
                                         RecipientRequirements)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex

RAW_CODES = [
    'A1',
    'A32',
    'B7',
    'B51',
    'DR11',
    'DR15'
]


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
                        HLAType(raw_code=RAW_CODES[0]),
                        HLAType(raw_code=RAW_CODES[1]),
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
                        HLAType(raw_code=RAW_CODES[1]),
                        HLAType(raw_code=RAW_CODES[2]),
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
                        HLAType(raw_code=RAW_CODES[1]),
                        HLAType(raw_code=RAW_CODES[2]),
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
                        HLAType(raw_code=RAW_CODES[4]),
                        HLAType(raw_code=RAW_CODES[5]),
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
