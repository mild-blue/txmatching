import time

from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import (
    Configuration, ForbiddenCountryCombination, ManualDonorRecipientScore)
from txmatching.database.services.config_service import (
    configuration_from_dict, get_latest_configuration_for_txm_event,
    save_configuration_to_db)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.enums import Country


class TestConfiguration(DbTests):
    def test_configuration(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        time.sleep(1)
        configuration = Configuration(
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)])
        save_configuration_to_db(configuration, txm_event, 1)
        self.assertEqual(Country.CZE, configuration.forbidden_country_combinations[0].donor_country)
        configuration = get_latest_configuration_for_txm_event(txm_event)
        self.assertEqual(Country.CZE, configuration.forbidden_country_combinations[0].donor_country)

    def test_configuration_from_dto(self):
        self.fill_db_with_patients_and_results()

        dto_dict = {'scorer_constructor_name': 'HLAAdditiveScorer',
                    'solver_constructor_name': 'AllSolutionsSolver',
                    'minimum_total_score': 0.0,
                    'maximum_total_score': 27.0,
                    'enforce_compatible_blood_group': False,
                    'forbidden_country_combinations': [{'donor_country': 'AUT', 'recipient_country': 'ISR'}],
                    'use_binary_scoring': False,
                    'max_cycle_length': 100,
                    'max_sequence_length': 100,
                    'max_number_of_distinct_countries_in_round': 100,
                    'required_patient_db_ids': [1, 3, 5],
                    'use_split_resolution': False,
                    'manual_donor_recipient_scores': [{'donor_db_id': 1, 'recipient_db_id': 0, 'score': 0.0}]}

        config = configuration_from_dict(dto_dict)
        self.assertEqual(Country.AUT, config.forbidden_country_combinations[0].donor_country)
        self.assertEqual([ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=0, score=0.0)],
                         config.manual_donor_recipient_scores, )
        self.assertEqual([1, 3, 5],
                         config.required_patient_db_ids, )

    def test_configuration_comparison(self):
        self.assertEqual(
            Configuration(),
            Configuration()
        )
        self.assertNotEqual(
            Configuration(max_cycle_length=5),
            Configuration(max_cycle_length=4)
        )
        self.assertNotEqual(
            Configuration(forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)]),
            Configuration(forbidden_country_combinations=[ForbiddenCountryCombination(Country.AUT, Country.CZE)])
        )
        self.assertEqual(
            Configuration(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
            ]),
            Configuration(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
            ])
        )
        self.assertEqual(
            Configuration(max_matchings_to_show_to_viewer=10),
            Configuration(max_matchings_to_show_to_viewer=20),
        )

        self.assertEqual(
            Configuration(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 2, 1),
                                                         ManualDonorRecipientScore(1, 3, 1)]),
            Configuration(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 3, 1),
                                                         ManualDonorRecipientScore(1, 2, 1)])
        )
