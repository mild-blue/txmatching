from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.services.config_service import \
    get_config_for_parameters_or_save
from txmatching.database.services.matching_service import \
    get_matchings_detailed_for_pairing_result_model
from txmatching.database.services.pairing_result_service import \
    get_pairing_result_comparable_to_config_or_solve
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.enums import Solver
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.logged_user import get_current_user_id


class MatchingService(DbTests):

    @staticmethod
    def fill_db_with_patients(file=get_absolute_path('/tests/resources/data.xlsx'), txm_event='test') -> int:
        patients = parse_excel_data(file, txm_event, None)
        txm_event = create_or_overwrite_txm_event(name=txm_event)
        replace_or_add_patients_from_excel(patients)
        return txm_event.db_id

    def test_matching_detailed_parameters(self):
        txm_event_id = self.fill_db_with_patients(get_absolute_path(PATIENT_DATA_OBFUSCATED))
        txm_event = get_txm_event_complete(txm_event_id)
        conf_dto = ConfigParameters(solver_constructor_name=Solver.AllSolutionsSolver,
                                    max_number_of_distinct_countries_in_round=1)
        user_id = get_current_user_id()

        # 1. Get or save config
        configuration = get_config_for_parameters_or_save(conf_dto, txm_event.db_id, user_id)

        # 2. Get or solve pairing result
        pairing_result_model = get_pairing_result_comparable_to_config_or_solve(configuration, txm_event)

        # 3. Get matchings detailed from pairing_result_model
        matchings_detailed = get_matchings_detailed_for_pairing_result_model(pairing_result_model, txm_event)

        self.assertEqual(matchings_detailed.number_of_possible_recipients, 12)
        self.assertEqual(matchings_detailed.number_of_possible_transplants, 157)
        self.assertEqual(matchings_detailed.max_transplant_score, 26)
