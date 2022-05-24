from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_hla_typing)
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
            etag=1,
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=create_hla_typing(
                    hla_types_list=[
                        _RAW_CODES[0],
                        _RAW_CODES[1],
                        'B44',
                        'DR10'
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985,
                note='donor note 1'
            ),
            related_recipient_db_id=None,
            donor_type=DonorType.DONOR,
            parsing_issues=[]
        ),
        Donor(
            db_id=2,
            medical_id='2',
            etag=1,
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=create_hla_typing(
                    hla_types_list=[
                        _RAW_CODES[1],
                        _RAW_CODES[2],
                        'DR10'
                    ]
                ),
                sex=Sex.M,
                height=180,
                year_of_birth=1985,
                note='donor note 2'
            ),
            related_recipient_db_id=None,
            donor_type=DonorType.DONOR,
            parsing_issues=[]
        )
    ]


def get_test_recipients():
    return [
        Recipient(
            db_id=3,
            medical_id='3',
            etag=1,
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=create_hla_typing(
                    hla_types_list=[
                        _RAW_CODES[1],
                        _RAW_CODES[2],
                        'DR1'
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985,
                note='recipient note 1'
            ),
            related_donors_db_ids=[1],
            acceptable_blood_groups=[],
            recipient_cutoff=None,
            hla_antibodies=create_antibodies([]),
            recipient_requirements=RecipientRequirements(
                max_donor_weight=50.5,
                max_donor_age=10,
                max_donor_height=150
            ),
            waiting_since=None,
            previous_transplants=None,
            parsing_issues=[]
        ),
        Recipient(
            db_id=4,
            medical_id='4',
            etag=1,
            parameters=PatientParameters(
                blood_group=BloodGroup.A,
                country_code=Country.CZE,
                hla_typing=create_hla_typing(
                    hla_types_list=[
                        'A3',
                        'B38',
                        _RAW_CODES[4],
                        _RAW_CODES[5],
                    ]
                ),
                sex=Sex.M,
                height=180,
                weight=70,
                year_of_birth=1985,
                note='recipient note 2'
            ),
            related_donors_db_ids=[1],
            acceptable_blood_groups=[],
            recipient_cutoff=None,
            hla_antibodies=create_antibodies([]),
            recipient_requirements=RecipientRequirements(
                min_donor_weight=100,
                min_donor_age=45,
                min_donor_height=190
            ),
            waiting_since=None,
            previous_transplants=None,
            parsing_issues=[]
        ),
    ]


def get_test_antibodies():
    return create_antibodies(
        hla_antibodies_list=[
            create_antibody('A7', 1200, 1000),
            create_antibody('B32', 1200, 1000),
            create_antibody('DR40', 1200, 1000),
            create_antibody('B5', 1200, 1000),
            create_antibody('DR9', 1200, 1000),
            create_antibody('A23', 1200, 1000)
        ]
    )
