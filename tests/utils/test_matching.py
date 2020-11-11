import unittest

from txmatching.patients.patient import (Donor, DonorType, Recipient,
                                         RecipientRequirements)
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntibody,
                                                    HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.scorers.matching import (
    get_count_of_transplants,
    get_matching_hla_typing,
    calculate_compatibility_index_for_group)
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.matching.transplant_cycle import TransplantCycle
from txmatching.solvers.matching.transplant_sequence import TransplantSequence
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, HLAGroups, Sex

RAW_CODES = [
    'A1',
    'A32',
    'B7',
    'B51',
    'DR11',
    'DR15'
]

DONORS = [
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
                    HLAType(raw_code="B44"),
                    HLAType(raw_code="DR10")
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
                    HLAType(raw_code="DR10")
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

RECIPIENTS = [
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
                    HLAType(raw_code="DR1")
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
                    HLAType(raw_code="A3"),
                    HLAType(raw_code="B38"),
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

TEST_ANTIGENS = [
    'A7',
    'B32',
    'DR40',
    'B5',
    'DR9',
    'A23'
]

TEST_ANTIBODIES = HLAAntibodies(
    hla_antibodies_list=[
        HLAAntibody('A7', 1200, 1000, 'A7'),
        HLAAntibody('B32', 1200, 1000, 'B32'),
        HLAAntibody('DR40', 1200, 1000, 'DR40'),
        HLAAntibody('B5', 1200, 1000, 'B5'),
        HLAAntibody('DR9', 1200, 1000, 'DR9'),
        HLAAntibody('A23', 1200, 1000, 'A23')
    ]
)


class TestMatching(unittest.TestCase):
    def test__get_matching_hla_typing(self):
        result = get_matching_hla_typing(DONORS[0], RECIPIENTS[0])
        result.sort()
        self.assertListEqual([RAW_CODES[1]], result)

        result = get_matching_hla_typing(DONORS[0], RECIPIENTS[1])
        result.sort()
        self.assertListEqual([], result)

        result = get_matching_hla_typing(DONORS[1], RECIPIENTS[0])
        result.sort()
        self.assertListEqual([RAW_CODES[1], RAW_CODES[2]], result)

        result = get_matching_hla_typing(DONORS[1], RECIPIENTS[1])
        result.sort()
        self.assertListEqual([], result)

    def test_calculate_antigen_score(self):
        # A32
        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroups.A)
        self.assertEquals(1, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroups.B)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[0], HLAGroups.DRB1)
        self.assertEquals(0, result)

        # No match
        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroups.A)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroups.B)
        self.assertEquals(0, result)

        result = calculate_compatibility_index_for_group(DONORS[0], RECIPIENTS[1], HLAGroups.DRB1)
        self.assertEquals(0, result)

        # A32, B7
        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroups.A)
        self.assertEquals(2, result)

        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroups.B)
        self.assertEquals(6, result)

        result = calculate_compatibility_index_for_group(DONORS[1], RECIPIENTS[0], HLAGroups.DRB1)
        self.assertEquals(0, result)

    def test_get_count_of_transplants(self):
        matching = MatchingWithScore(
            donor_recipient_pairs=frozenset(),
            score=0,
            order_id=0
        )

        result = get_count_of_transplants(matching)
        self.assertEquals(0, result)

        matching = MatchingWithScore(
            donor_recipient_pairs=frozenset(),
            score=0,
            order_id=0
        )

        matching._cycles = [
            TransplantCycle(donor_recipient_pairs=[DonorRecipientPair(DONORS[0], RECIPIENTS[0])]),
            TransplantCycle(donor_recipient_pairs=[]),
            TransplantCycle(donor_recipient_pairs=[
                DonorRecipientPair(DONORS[0], RECIPIENTS[0]),
                DonorRecipientPair(DONORS[1], RECIPIENTS[1]),
            ]),
        ]

        matching._sequences = [
            TransplantSequence(donor_recipient_pairs=[
                DonorRecipientPair(DONORS[0], RECIPIENTS[0]),
            ])
        ]

        result = get_count_of_transplants(matching)
        self.assertEquals(4, result)

