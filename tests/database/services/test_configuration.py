from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import (
    ConfigParameters, ForbiddenCountryCombination, ManualDonorRecipientScore)
from txmatching.database.services.config_service import (
    configuration_parameters_from_dict,
    get_configuration_parameters_from_db_id_or_default,
    save_config_parameters_to_db, set_config_as_default)
from txmatching.database.services.txm_event_service import (
    get_txm_event_base, get_txm_event_complete)
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import Solver


class TestConfiguration(DbTests):
    def test_configuration(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_complete(txm_event_db_id)
        configuration_parameters_expected = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)])
        configuration_actual = save_config_parameters_to_db(configuration_parameters_expected, txm_event.db_id, 1)

        self.assertEqual(configuration_parameters_expected, configuration_actual.parameters)

    def test_default_configuration(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        txm_event = get_txm_event_base(txm_event_db_id)
        configuration_parameters_expected = ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)])
        self.assertNotEqual(ConfigParameters(), configuration_parameters_expected)
        configuration = save_config_parameters_to_db(configuration_parameters_expected, txm_event.db_id, 1)

        actual_configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, None)
        self.assertEqual(ConfigParameters(), actual_configuration_parameters)

        set_config_as_default(txm_event.db_id, configuration.id)
        txm_event = get_txm_event_base(txm_event_db_id)

        actual_configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, None)
        self.assertEqual(configuration_parameters_expected, actual_configuration_parameters)

    def test_configuration_from_dto(self):
        self.fill_db_with_patients_and_results()

        dto_dict = {'scorer_constructor_name': 'SplitScorer',
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

        config = configuration_parameters_from_dict(dto_dict)
        self.assertEqual(Country.AUT, config.forbidden_country_combinations[0].donor_country)
        self.assertEqual([ManualDonorRecipientScore(donor_db_id=1, recipient_db_id=0, score=0.0)],
                         config.manual_donor_recipient_scores, )
        self.assertEqual([1, 3, 5],
                         config.required_patient_db_ids, )

    def test_configuration_comparison(self):
        self.assertFalse(
            ConfigParameters(max_cycle_length=5).comparable(
                ConfigParameters(max_cycle_length=4))
        )
        self.assertFalse(ConfigParameters(
            forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)]).comparable(
            ConfigParameters(forbidden_country_combinations=[ForbiddenCountryCombination(Country.AUT, Country.CZE)]))
        )
        self.assertTrue(
            ConfigParameters(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
            ]).comparable(
                ConfigParameters(forbidden_country_combinations=[
                    ForbiddenCountryCombination(Country.ISR, Country.CAN),
                    ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ])
            )
        )
        self.assertTrue(
            ConfigParameters(max_matchings_to_show_to_viewer=10).comparable(
                ConfigParameters(max_matchings_to_show_to_viewer=20)
            )
        )

        self.assertTrue(
            ConfigParameters(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 2, 1),
                                                            ManualDonorRecipientScore(1, 3, 1)]).comparable(
                ConfigParameters(manual_donor_recipient_scores=[ManualDonorRecipientScore(1, 3, 1),
                                                                ManualDonorRecipientScore(1, 2, 1)])
            )
        )

        self.assertTrue(ConfigParameters().comparable(ConfigParameters()))
        self.assertTrue(ConfigParameters(max_matchings_in_all_solutions_solver=10).comparable(
            ConfigParameters(max_matchings_in_all_solutions_solver=100)))
        self.assertFalse(ConfigParameters(max_matchings_in_all_solutions_solver=100).comparable(
            ConfigParameters(max_matchings_in_all_solutions_solver=10)))
        self.assertTrue(
            ConfigParameters(required_patient_db_ids=[2, 1]).comparable(ConfigParameters(required_patient_db_ids=[1, 2])))
        self.assertFalse(
            ConfigParameters(required_patient_db_ids=[1]).comparable(ConfigParameters(required_patient_db_ids=[1, 2])))

    def test_configuration_non_negative_parameter(self):
        with self.assertRaises(ValueError):
            ConfigParameters(minimum_total_score=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(blood_group_compatibility_bonus=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_cycle_length=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_sequence_length=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_number_of_distinct_countries_in_round=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_debt_for_country=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_debt_for_country_for_blood_group_zero=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_matchings_to_show_to_viewer=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_number_of_matchings=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_matchings_in_all_solutions_solver=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_cycles_in_all_solutions_solver=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_matchings_in_ilp_solver=-1)
        with self.assertRaises(ValueError):
            ConfigParameters(max_number_of_dynamic_constrains_ilp_solver=-1)

    def test_configuration_equality(self):
        self.assertNotEqual(
            ConfigParameters(max_cycle_length=5),
            ConfigParameters(max_cycle_length=4)
        )
        self.assertNotEqual(
            ConfigParameters(
                forbidden_country_combinations=[ForbiddenCountryCombination(Country.CZE, Country.AUT)]
            ),
            ConfigParameters(
                forbidden_country_combinations=[ForbiddenCountryCombination(Country.AUT, Country.CZE)]
            )
        )
        self.assertNotEqual(
            ConfigParameters(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
            ]),
            ConfigParameters(forbidden_country_combinations=[
                ForbiddenCountryCombination(Country.ISR, Country.CAN),
                ForbiddenCountryCombination(Country.CZE, Country.AUT),
            ])
        )
        self.assertNotEqual(
            ConfigParameters(max_matchings_to_show_to_viewer=10),
            ConfigParameters(max_matchings_to_show_to_viewer=20)
        )

        self.assertEqual(
            ConfigParameters(),
            ConfigParameters()
        )
        self.assertEqual(
            ConfigParameters(max_matchings_to_show_to_viewer=20),
            ConfigParameters(max_matchings_to_show_to_viewer=20)
        )
