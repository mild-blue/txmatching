from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.web import API_VERSION


class TestOptimizerApi(DbTests):

    def test_optimizer_api_works(self):
        with self.app.test_client() as client:
            json_data = {
                "compatibility_graph": [
                    {
                        "donor_index": 1,
                        "recipient_index": 2,
                        "hla_compatibility_score": 17,
                        "donor_age_difference": 1
                    },
                    {
                        "donor_index": 2,
                        "recipient_index": 4,
                        "hla_compatibility_score": -1,
                        "donor_age_difference": 4
                    },
                    {
                        "donor_index": 3,
                        "recipient_index": 4,
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
                        "donor_id": 3,
                        "recipient_id": 7
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
            res = client.post(f'{API_VERSION}/optimizer',
                              headers=self.auth_headers, json=json_data)

        self.assertEqual(200, res.status_code)
        # TODO: test for proper return after completing optimizer endpoint functionality
