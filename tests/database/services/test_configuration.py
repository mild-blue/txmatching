import time

from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import (
    Configuration, ForbiddenCountryCombination, ManualDonorRecipientScore)
from txmatching.database.services.config_service import (
    configuration_from_dict, get_latest_configuration_for_txm_event,
    save_configuration_to_db)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.country_enum import Country


class TestConfiguration(DbTests):
    def test_configuration(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        time.sleep(1)
        configuration = Configuration(
            solver_constructor_name='AllSolutionsSolver',
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)])
        save_configuration_to_db(configuration, txm_event, 1)
        self.assertEqual(Country.CZE, configuration.forbidden_country_combinations[0].donor_country)
        configuration = get_latest_configuration_for_txm_event(txm_event)
        self.assertEqual(Country.CZE, configuration.forbidden_country_combinations[0].donor_country)

    def test_configuration_from_dto(self):
        self.fill_db_with_patients_and_results()

        dto_dict = {'scorer_constructor_name': 'SplitHLAAdditiveScorer',
                    'solver_constructor_name': 'AllSolutionsSolver',
                    'minimum_total_score': 0.0,
                    'enforce_compatible_blood_group': False,
                    'forbidden_country_combinations': [{'donor_country': 'AUT', 'recipient_country': 'ISR'}],
                    'use_binary_scoring': False,
                    'max_cycle_length': 100,
                    'max_sequence_length': 100,
                    'max_number_of_distinct_countries_in_round': 100,
                    'required_patient_db_ids': [1, 3, 5],
                    'use_high_resolution': False,
                    'manual_donor_recipient_scores': [{'donor_db_id': 1, 'recipient_db_id': 0, 'score': 0.0}]}

        config = configuration_from_dict(dto_dict)
        self.assertEqual(Country.AUT, config.forbidden_country_combinations[0].donor_country)
        self.assertEqual([ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=0, score=0.0)],
                         config.manual_donor_recipient_scores, )
        self.assertEqual([1, 3, 5],
                         config.required_patient_db_ids, )

    def test_configuration_comparison(self):
        self.assertFalse(
            Configuration(max_cycle_length=5).comparable(
                Configuration(max_cycle_length=4))
        )
        self.assertFalse(Configuration(
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)]).comparable(
            Configuration(forbidden_country_combinations=[ForbiddenCountryCombination(Country.AUT, Country.CZE)]))
        )
        self.assertTrue(
            Configuration(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
            ]).comparable(
                Configuration(forbidden_country_combinations=[
                    ForbiddenCountryCombination(Country.ISR, Country.CAN),
                    ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ])
            )
        )
        self.assertTrue(
            Configuration(max_matchings_to_show_to_viewer=10).comparable(
                Configuration(max_matchings_to_show_to_viewer=20)
            )
        )

        self.assertTrue(
            Configuration(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 2, 1),
                                                         ManualDonorRecipientScore(1, 3, 1)]).comparable(
                Configuration(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 3, 1),
                                                             ManualDonorRecipientScore(1, 2, 1)])
            )
        )

        self.assertTrue(Configuration().comparable(Configuration()))
        self.assertTrue(Configuration(max_matchings_in_all_solutions_solver=10).comparable(
            Configuration(max_matchings_in_all_solutions_solver=100)))
        self.assertFalse(Configuration(max_matchings_in_all_solutions_solver=100).comparable(
            Configuration(max_matchings_in_all_solutions_solver=10)))
        self.assertTrue(
            Configuration(required_patient_db_ids=[2, 1]).comparable(Configuration(required_patient_db_ids=[1, 2])))
        self.assertFalse(
            Configuration(required_patient_db_ids=[1]).comparable(Configuration(required_patient_db_ids=[1, 2])))
