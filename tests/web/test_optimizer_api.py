from local_testing_utilities.generate_patients import (
    GENERATED_TXM_EVENT_NAME, SMALL_DATA_FOLDER,
    SMALL_DATA_FOLDER_MULTIPLE_DONORS, store_generated_patients_from_folder)
from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete, get_txm_event_db_id_by_name
from txmatching.optimizer.optimizer_functions import get_compatibility_graph
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.web import API_VERSION, OPTIMIZER_NAMESPACE
from txmatching.utils.enums import Solver
from txmatching.utils.get_absolute_path import get_absolute_path

class TestOptimizerApi(DbTests):

    def test_optimizer_api_works(self):
        with self.app.test_client() as client:
            json_data = {
                "compatibility_graph": [
                    {
                        "donor_id": 1,
                        "recipient_id": 2,
                        "hla_compatibility_score": 17,
                        "donor_age_difference": 1
                    },
                    {
                        "donor_id": 3,
                        "recipient_id": 4,
                        "hla_compatibility_score": 10,
                        "donor_age_difference": 17
                    }
                ],
                "pairs": [
                    {
                        "donor_id": 1,
                        "recipient_id": 4
                    },
                    {
                        "donor_id": 2,
                        "recipient_id": 2
                    },
                    {
                        "donor_id": 3
                    }
                ],
                "configuration": {
                    "limitations": {
                        "max_cycle_length": 3,
                        "max_chain_length": 4,
                        "custom_algorithm_settings": {
                            "max_number_of_iterations": 200
                        }
                    },
                    "scoring": [
                        [
                            {
                                "transplant_count": 1
                            }
                        ],
                        [
                            {
                                "hla_compatibility_score": 3
                            },
                            {
                                "donor_age_difference": 10
                            }
                        ]
                    ]
                }
            }
            res = client.post(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}',
                              headers=self.auth_headers, json=json_data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(1, res.json['statistics']['number_of_found_cycles_and_chains'])
        self.assertEqual(2, res.json['statistics']['number_of_found_transplants'])

        total_score = sum([dic["hla_compatibility_score"] for dic in json_data["compatibility_graph"]])
        self.assertEqual(total_score, res.json['cycles_and_chains'][0]['scores'][0])
        self.assertGreaterEqual(total_score, 0)

    def test_optimizer_api_gives_same_solution_as_ilp_solver_itself_small_data_folder(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER)
        txm_event_db_id = get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME)
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                max_sequence_length=4,
                max_cycle_length=4,
                max_number_of_matchings=1)

        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)

        with self.app.test_client() as client:
            # export the current event
            temp_res = client.get(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}/export/{txm_event_db_id}/default',
                             headers=self.auth_headers)
            # compute the solution
            res = client.post(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}', headers=self.auth_headers, json=temp_res.json)

        total_score = sum([dic["scores"][0] for dic in res.json["cycles_and_chains"]])
        self.assertEqual(solutions[0].score, total_score)
        self.assertGreaterEqual(total_score, 0)

        self.assertGreaterEqual(res.json['statistics']['number_of_found_cycles_and_chains'], 1)
        self.assertGreaterEqual(res.json['statistics']['number_of_found_transplants'], 1)

    def test_optimizer_api_gives_same_solution_as_ilp_solver_itself_multiple_donors(self):
        store_generated_patients_from_folder(SMALL_DATA_FOLDER_MULTIPLE_DONORS)
        txm_event_db_id = get_txm_event_db_id_by_name(GENERATED_TXM_EVENT_NAME)
        txm_event = get_txm_event_complete(txm_event_db_id)
        config_parameters = ConfigParameters(
                solver_constructor_name=Solver.ILPSolver,
                max_sequence_length=4,
                max_cycle_length=4,
                max_number_of_matchings=1)

        solutions = list(solve_from_configuration(config_parameters, txm_event).calculated_matchings_list)

        with self.app.test_client() as client:
            # export the current event
            temp_res = client.get(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}/export/{txm_event_db_id}/default',
                             headers=self.auth_headers)
            # compute the solution
            res = client.post(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}',
                              headers=self.auth_headers, json=temp_res.json)

        total_score = sum([dic["scores"][0] for dic in res.json["cycles_and_chains"]])
        self.assertEqual(solutions[0].score, total_score)

    def test_optimizer_export_api_works(self):
        txm_event_db_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_db_id)

        with self.app.test_client() as client:
            res = client.get(f'{API_VERSION}/{OPTIMIZER_NAMESPACE}/export/{txm_event_db_id}/default',
                             headers=self.auth_headers)

        self.assertEqual(200, res.status_code)

        # number of pairs in response equal to the number of active and valid pairs in txm event
        self.assertEqual(len(txm_event.active_and_valid_donors_dict), len(res.json['pairs']))

        compatibility_graph = get_compatibility_graph(txm_event.active_and_valid_donors_dict,
                                                      txm_event.active_and_valid_recipients_dict)
        self.assertCountEqual(compatibility_graph, res.json['compatibility_graph'])

        # we are calling txm event with default configuration
        def_config = ConfigParameters()
        self.assertEqual(def_config.max_sequence_length, res.json['configuration']['limitations']['max_chain_length'])
        self.assertEqual(def_config.max_cycle_length, res.json['configuration']['limitations']['max_cycle_length'])
