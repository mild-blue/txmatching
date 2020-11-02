from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import (
    HLAAntibodiesDTO, HLAAntibodyDTO)
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import (
    HLATypeUpdateDTO, HLATypingUpdateDTO)
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.db import db
from txmatching.database.services.patient_service import (
    save_patients_from_excel_to_txm_event, update_donor, update_recipient)
from txmatching.database.sql_alchemy_schema import (
    AppUserModel, ConfigModel, DonorModel, PairingResultModel,
    RecipientAcceptableBloodModel, RecipientHLAAntibodyModel, RecipientModel)
from txmatching.patients.patient import RecipientRequirements
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.logged_user import get_current_user_id


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients_from_obfuscated_excel(self):
        patients = parse_excel_data(get_absolute_path('tests/resources/patient_data_2020_07_obfuscated.xlsx'))
        txm_event = create_or_overwrite_txm_event('test')

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

        save_patients_from_excel_to_txm_event(patients, txm_event.db_id)

        configs = ConfigModel.query.all()
        recipients = RecipientModel.query.all()
        donors = DonorModel.query.all()
        pairing_results = PairingResultModel.query.all()
        recipient_acceptable_bloods = RecipientAcceptableBloodModel.query.all()
        recipient_hla_antibodies = RecipientHLAAntibodyModel.query.all()
        app_users = AppUserModel.query.all()

        self.assertEqual(0, len(configs))
        self.assertEqual(34, len(recipients))
        self.assertEqual(38, len(donors))
        self.assertEqual(0, len(pairing_results))
        self.assertEqual(91, len(recipient_acceptable_bloods))
        self.assertEqual(1102, len(recipient_hla_antibodies))
        self.assertEqual(5, len(app_users))

        self.assertEqual(
            572,
            len(list(solve_from_configuration(Configuration(
                max_cycle_length=100,
                max_sequence_length=100,
                max_number_of_distinct_countries_in_round=100),
                txm_event.db_id).calculated_matchings)
                )
        )

    def test_update_recipient(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({'0', 'A'}, {blood.blood_type for blood in RecipientModel.query.get(1).acceptable_blood})
        self.assertSetEqual({'B7', 'DQ6', 'DQ5'},
                            {hla_antibody.code for hla_antibody in RecipientModel.query.get(1).hla_antibodies})
        self.assertFalse(
            RecipientModel.query.get(1).recipient_requirements['require_better_match_in_compatibility_index'])
        update_recipient(RecipientUpdateDTO(
            acceptable_blood_groups=['AB'],
            hla_antibodies=HLAAntibodiesDTO([HLAAntibodyDTO(mfi=20, raw_code='B42'),
                                             HLAAntibodyDTO(mfi=20, raw_code='DQ[01:03,      06:03]')
                                             ]),
            hla_typing=HLATypingUpdateDTO([
                HLATypeUpdateDTO('A11'),
                HLATypeUpdateDTO('DQ[01:03,      06:03]')
            ]),
            recipient_requirements=RecipientRequirements(require_better_match_in_compatibility_index=True),
            db_id=1
        ), txm_event_db_id)

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(0, len(configs))

        self.assertSetEqual({'AB'}, {blood.blood_type for blood in RecipientModel.query.get(1).acceptable_blood})
        self.assertSetEqual({'B42', 'DQ6', 'DQA1'}, {code.code for code in RecipientModel.query.get(1).hla_antibodies})
        self.assertTrue(
            RecipientModel.query.get(1).recipient_requirements['require_better_match_in_compatibility_index'])
        self.assertSetEqual({'A11', 'DQ6', 'DQA1'},
                            {hla_type['code'] for hla_type in RecipientModel.query.get(1).hla_typing['hla_types_list']})

    def test_update_donor(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({'A11',
                             'B8',
                             'DR11'},
                            {hla_type['code'] for hla_type in DonorModel.query.get(1).hla_typing['hla_types_list']})

        update_donor(DonorUpdateDTO(
            hla_typing=HLATypingUpdateDTO([
                HLATypeUpdateDTO('A11'),
                HLATypeUpdateDTO('DQ[01:03,      06:03]')
            ]),
            db_id=1
        ), txm_event_db_id)

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(0, len(configs))

        self.assertSetEqual({'A11', 'DQ6', 'DQA1'},
                            {hla_type['code'] for hla_type in DonorModel.query.get(1).hla_typing['hla_types_list']})
