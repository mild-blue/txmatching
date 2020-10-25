import unittest

from txmatching.patients.patient import Donor, Recipient, DonorType, RecipientRequirements
from txmatching.patients.patient_parameters import PatientParameters, HLATyping, HLAType, HLAAntibodies
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.solvers.matching.transplant_cycle import TransplantCycle
from txmatching.solvers.matching.transplant_sequence import TransplantSequence
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex, HLATypes
from txmatching.utils.matching import get_matching_hla_typing, calculate_antigen_score, get_count_of_transplants

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
        medical_id="1",
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=HLATyping(
                hla_types_list=[
                    HLAType(raw_code=RAW_CODES[0]),
                    HLAType(raw_code=RAW_CODES[1]),
                ]
            ),
            sex=Sex.M,
            height=180,
            weight=70,
            yob=1985
        ),
        related_recipient_db_id=None,
        donor_type=DonorType.DONOR
    ),
    Donor(
        db_id=2,
        medical_id="2",
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=HLATyping(
                hla_types_list=[
                    HLAType(raw_code=RAW_CODES[1]),
                    HLAType(raw_code=RAW_CODES[2]),
                ]
            ),
            sex=Sex.M,
            height=180,
            weight=70,
            yob=1985
        ),
        related_recipient_db_id=None,
        donor_type=DonorType.DONOR
    )
]

RECIPIENTS = [
    Recipient(
        db_id=3,
        medical_id="3",
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=HLATyping(
                hla_types_list=[
                    HLAType(raw_code=RAW_CODES[1]),
                    HLAType(raw_code=RAW_CODES[2]),
                ]
            ),
            sex=Sex.M,
            height=180,
            weight=70,
            yob=1985
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
        medical_id="4",
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=HLATyping(
                hla_types_list=[
                    HLAType(raw_code=RAW_CODES[4]),
                    HLAType(raw_code=RAW_CODES[5]),
                ]
            ),
            sex=Sex.M,
            height=180,
            weight=70,
            yob=1985
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


class TestMatching(unittest.TestCase):
    def test_get_matching_hla_typing(self):
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
        result = calculate_antigen_score(DONORS[0], RECIPIENTS[0], HLATypes.A)
        self.assertEquals(1, result)

        result = calculate_antigen_score(DONORS[0], RECIPIENTS[0], HLATypes.B)
        self.assertEquals(0, result)

        result = calculate_antigen_score(DONORS[0], RECIPIENTS[0], HLATypes.DR)
        self.assertEquals(0, result)

        # No match
        result = calculate_antigen_score(DONORS[0], RECIPIENTS[1], HLATypes.A)
        self.assertEquals(0, result)

        result = calculate_antigen_score(DONORS[0], RECIPIENTS[1], HLATypes.B)
        self.assertEquals(0, result)

        result = calculate_antigen_score(DONORS[0], RECIPIENTS[1], HLATypes.DR)
        self.assertEquals(0, result)

        # A32, B7
        result = calculate_antigen_score(DONORS[1], RECIPIENTS[0], HLATypes.A)
        self.assertEquals(1, result)

        result = calculate_antigen_score(DONORS[1], RECIPIENTS[0], HLATypes.B)
        self.assertEquals(3, result)

        result = calculate_antigen_score(DONORS[1], RECIPIENTS[0], HLATypes.DR)
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
