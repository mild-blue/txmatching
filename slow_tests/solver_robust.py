
import json

from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.configuration.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.database.services.txm_event_service import (
    get_txm_event, remove_donors_and_recipients_from_txm_event_for_country)
from txmatching.database.sql_alchemy_schema import (
    AppUserModel, ConfigModel, DonorModel, PairingResultModel,
    RecipientAcceptableBloodModel, RecipientHLAAntibodyModel, RecipientModel)
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.enums import Country
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.logged_user import get_current_user_id


class TestLargeMatchingDoesNotFail(DbTests):
    def testing_computation_for_patients_that_create_extremely_many_matchings(self):
        txm_event = create_or_overwrite_txm_event('test')
        patients = parse_excel_data(get_absolute_path('/tests/resources/data2.xlsx'), txm_event.name, None)
        replace_or_add_patients_from_excel(patients)
        patients = parse_excel_data(get_absolute_path(PATIENT_DATA_OBFUSCATED), txm_event.name, None)
        replace_or_add_patients_from_excel(patients)

        txm_event = get_txm_event(txm_event.db_id)

        self.assertEqual(42, len(txm_event.all_donors))
        solve_from_configuration(Configuration(), txm_event.db_id)
