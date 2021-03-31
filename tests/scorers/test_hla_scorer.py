from typing import List

from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_hla_typing)
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.high_res_hla_additive_scorer import HighResScorer
from txmatching.scorers.high_res_other_hla_types_additive_scorer import \
    HighResWithDQDPScorer
from txmatching.scorers.split_hla_additive_scorer import SplitScorer
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country


class TestHlaScorer(DbTests):
    split_scorer = SplitScorer()
    high_res_scorer = HighResScorer()
    high_res_other_hla_types_scorer = HighResWithDQDPScorer()

    def test_scorer_max_scores(self):
        self.assertEqual(26, self.split_scorer.max_transplant_score)
        self.assertEqual(18, self.high_res_scorer.max_transplant_score)
        self.assertEqual(54, self.high_res_other_hla_types_scorer.max_transplant_score)

    def test_scorers_on_some_patients(self):
        donor = _create_donor(['A*01:01', 'A3', 'B7', 'B37', 'DR11', 'DR15', 'DR52', 'DR51', 'DQ7', 'DQ6'])
        recipient = _create_recipient(['A*01:01', 'A2', 'B27', 'B37', 'DR1', 'DR10', 'DQ6'])
        original_donor = _create_donor([])

        self.assertEqual(4, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                               original_donor=original_donor))
        self.assertEqual(5, self.high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                  original_donor=original_donor))

        self.assertEqual(7, self.high_res_other_hla_types_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                                  original_donor=original_donor))

    def test_scorers_on_some_other_patients(self):
        with self.app.test_client():
            donor = _create_donor(
                ['A*01:01', 'A23', 'B7', 'B37', 'DR11', 'DR15', 'DR52', 'DR51', 'DQ7', 'DQ6', 'DPA1*01:03'])
            recipient = _create_recipient(['A*01:01', 'A9', 'B27', 'B37', 'DR1', 'DR10', 'DQ6', 'DPA1*01:04'])
            original_donor = _create_donor([])

            self.assertEqual(5, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))
            self.assertEqual(6, self.high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                      original_donor=original_donor))

            self.assertEqual(10, self.high_res_other_hla_types_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                                       original_donor=original_donor))

    def test_scorers_duplicate_gene_of_donor(self):
        with self.app.test_client():
            donor = _create_donor(['A*01:01'])
            recipient = _create_recipient(['A*01:01', 'A9'])
            original_donor = _create_donor([])

            self.assertEqual(2, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))
            self.assertEqual(6, self.high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                      original_donor=original_donor))

            self.assertEqual(6, self.high_res_other_hla_types_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                                      original_donor=original_donor))

    def test_scorers_duplicate_gene_of_recipient(self):
        with self.app.test_client():
            donor = _create_donor(['A*01:01', 'A9'])
            recipient = _create_recipient(['A*01:01'])
            original_donor = _create_donor([])

            self.assertEqual(1, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))
            self.assertEqual(3, self.high_res_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                      original_donor=original_donor))

            self.assertEqual(3, self.high_res_other_hla_types_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                                      original_donor=original_donor))

    def test_another_duplicate(self):
        with self.app.test_client():
            donor = _create_donor(['A2', 'B62', 'B61', 'DR4', 'DR13', 'DR52', 'DR53', 'DQ6', 'DQ8'])
            recipient = _create_recipient(['A1', 'A2', 'B27', 'B37', 'DR1', 'DR10'])
            original_donor = _create_donor([])

            self.assertEqual(2, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))

    def test_match_in_broad(self):
        # 22 vs 25
        with self.app.test_client():
            donor = _create_donor(['B51', 'B52'])
            recipient = _create_recipient(['B7', 'B51'])
            original_donor = _create_donor([])

            self.assertEqual(6, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))
            donor = _create_donor(['A25', 'A26'])
            recipient = _create_recipient(['A1', 'A26'])
            original_donor = _create_donor([])

            self.assertEqual(2, self.split_scorer.score_transplant(donor=donor, recipient=recipient,
                                                                   original_donor=original_donor))


def _create_donor(hla_typing: List[str]):
    return Donor(
        db_id=-1,
        medical_id='original_donor',
        related_recipient_db_id=1,
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=create_hla_typing(
                hla_typing
            )
        )
    )


def _create_recipient(hla_typing: List[str]):
    return Recipient(
        db_id=1,
        acceptable_blood_groups=[],
        related_donor_db_id=1,
        medical_id='recipient',
        parameters=PatientParameters(
            blood_group=BloodGroup.A,
            country_code=Country.CZE,
            hla_typing=create_hla_typing(hla_typing)
        ),
        hla_antibodies=create_antibodies([])
    )
