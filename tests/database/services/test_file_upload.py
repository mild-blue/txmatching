import json

from local_testing_utilities.populate_db import PATIENT_DATA_OBFUSCATED
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.database.db import db
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_excel
from txmatching.database.services.txm_event_service import (
    get_txm_event_complete,
    remove_donors_and_recipients_from_txm_event_for_country)
from txmatching.database.sql_alchemy_schema import (
    AppUserModel, ConfigModel, DonorModel, HLAAntibodyRawModel,
    PairingResultModel, RecipientAcceptableBloodModel, RecipientModel)
from txmatching.scorers.split_hla_additive_scorer import SplitScorer
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLACrossmatchLevel, Solver
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.logged_user import get_current_user_id


class TestUpdateDonorRecipient(DbTests):
    def test_saving_patients_from_obfuscated_excel(self):
        txm_event = create_or_overwrite_txm_event('test')
        patients = parse_excel_data(
            get_absolute_path(PATIENT_DATA_OBFUSCATED),
            txm_event.name,
            None)

        # Insert config and validates that it is stored into DB
        user_id = get_current_user_id()
        config = ConfigModel(
            txm_event_id=txm_event.db_id,
            parameters={},
            created_by=user_id
        )

        db.session.add(config)
        db.session.commit()
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(1, len(configs))

        replace_or_add_patients_from_excel(patients)

        configs = ConfigModel.query.all()
        recipients = RecipientModel.query.all()
        donors = DonorModel.query.all()
        pairing_results = PairingResultModel.query.all()
        recipient_acceptable_bloods = RecipientAcceptableBloodModel.query.all()
        hla_antibodies_raw = HLAAntibodyRawModel.query.all()
        app_users = AppUserModel.query.all()

        txm_event = get_txm_event_complete(txm_event.db_id)

        recipients_tuples = [(
            recipient.medical_id,
            recipient.parameters.country_code,
            recipient.parameters.blood_group,
            [hla_code.code.display_code for hla_group in recipient.hla_antibodies.hla_antibodies_per_groups
             for hla_code in hla_group.hla_antibody_list],
            [hla_code.code.display_code for hla_group in recipient.parameters.hla_typing.hla_per_groups
             for hla_code in hla_group.hla_types],
            recipient.acceptable_blood_groups
        )
            for recipient in txm_event.active_and_valid_recipients_dict.values()]

        donors_tuples = [(
            donor.medical_id,
            donor.parameters.country_code,
            donor.parameters.blood_group,
            [hla_code.code.display_code for hla_group in donor.parameters.hla_typing.hla_per_groups
             for hla_code in hla_group.hla_types],
            txm_event.active_and_valid_recipients_dict[
                donor.related_recipient_db_id].medical_id if donor.related_recipient_db_id else ''
        )
            for donor in txm_event.active_and_valid_donors_dict.values()]

        self.assertEqual(1, len(configs))
        self.assertEqual(34, len(recipients))
        self.assertEqual(38, len(donors))
        self.assertEqual(3, len({donor.country for donor in donors}))
        self.assertEqual(3, len({recipient.country for recipient in recipients}))
        self.assertEqual(0, len(pairing_results))
        self.assertEqual(91, len(recipient_acceptable_bloods))
        self.assertEqual(1059, len(hla_antibodies_raw))
        self.assertEqual(7, len(app_users))

        all_matchings = list(solve_from_configuration(ConfigParameters(
            solver_constructor_name=Solver.AllSolutionsSolver,
            max_cycle_length=100,
            max_sequence_length=100,
            max_number_of_distinct_countries_in_round=100,
            use_high_resolution=True,
            max_number_of_matchings=1000,
            max_debt_for_country=10,
            hla_crossmatch_level=HLACrossmatchLevel.NONE,
        ),
            txm_event).calculated_matchings_list)
        self.assertEqual(961, len(all_matchings))

        self.maxDiff = None

        scorer = SplitScorer()
        calculated_scores = scorer.get_compatibility_graph(txm_event.active_and_valid_recipients_dict,
                                                           txm_event.active_and_valid_donors_dict)

        # This commented out code serves the purpose to re-create the files in case something in the data changes
        # with open(get_absolute_path('tests/resources/recipients_tuples.json'), 'w') as f:
        #     json.dump(recipients_tuples, f)
        # with open(get_absolute_path('tests/resources/donors_tuples.json'), 'w') as f:
        #     json.dump(donors_tuples, f)
        # with open(get_absolute_path('tests/resources/score.json'), 'w') as f:
        #     json.dump(calculated_score.tolist(), f)

        with open(get_absolute_path('tests/resources/recipients_tuples.json')) as f:
            expected_recipients_tuples = json.load(f)
        with open(get_absolute_path('tests/resources/donors_tuples.json')) as f:
            expected_donors_tuples = json.load(f)
        with open(get_absolute_path('tests/resources/score.json')) as f:
            expected_scores = json.load(f)

        expected_recipients_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]),
                                       frozenset(tup[4]), frozenset(tup[5])
                                       ) for tup in expected_recipients_tuples]
        recipients_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]),
                              frozenset(tup[4]), frozenset(tup[5])
                              ) for tup in recipients_tuples]

        expected_donors_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]), tup[4]) for tup in
                                  expected_donors_tuples]
        donors_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]), tup[4]) for tup in donors_tuples]

        for i, recipient in enumerate(recipients_tuples):
            self.assertTrue(recipient in expected_recipients_tuples, f'Error in round {i}: {recipient} not found')

        for i, donor in enumerate(donors_tuples):
            self.assertTrue(donor in expected_donors_tuples, f'Error in round {i}: {donor} not found')

        donor_enums = [i for i in range(0, len(txm_event.active_and_valid_donors_dict))]
        recipient_enums = [i for i in range(0, len(txm_event.active_and_valid_recipients_dict))]
        for donor_enum, donor, expected_score_row in zip(donor_enums, txm_event.active_and_valid_donors_dict.values(),
                                                         expected_scores):
            for recipient_enum, recipient, expected_score in zip(
                recipient_enums, txm_event.active_and_valid_recipients_dict.values(), expected_score_row):
                if expected_score >= 0: 
                    calculated_score = calculated_scores[(donor_enum, recipient_enum)]
                    self.assertEqual(expected_score, calculated_score,
                                     f'Not true for expected {expected_score} vs real {calculated_score} '
                                     f'{[code.raw_code for code in donor.parameters.hla_typing.hla_types_raw_list]} and '
                                     f'{[code.raw_code for code in recipient.parameters.hla_typing.hla_types_raw_list]}')

    def test_loading_patients_wrong(self):
        txm_event = create_or_overwrite_txm_event('test')
        self.assertRaises(InvalidArgumentException, lambda: parse_excel_data(
            get_absolute_path('tests/resources/patient_data_wrong.xlsx'),
            txm_event.name,
            None))
        self.assertRaises(InvalidArgumentException, lambda: parse_excel_data(
            get_absolute_path('tests/resources/nonexistent_file.xlsx'),
            txm_event.name,
            None))
        self.assertRaises(InvalidArgumentException, lambda: parse_excel_data(
            get_absolute_path('tests/resources/patient_data_issues.xlsx'),
            txm_event.name,
            None))

    def test_remove_patients(self):
        txm_event_db_id = self.fill_db_with_patients(file=get_absolute_path(PATIENT_DATA_OBFUSCATED))
        remove_donors_and_recipients_from_txm_event_for_country(txm_event_db_id, Country.IND)
        txm_event = get_txm_event_complete(txm_event_db_id)
        country_donors = [donor for donor in txm_event.active_and_valid_donors_dict.values() if
                          donor.parameters.country_code == Country.IND]
        self.assertEqual(0, len(country_donors))
        self.assertEqual(26, len(txm_event.active_and_valid_donors_dict))
        self.assertEqual(25, len(txm_event.active_and_valid_recipients_dict))
