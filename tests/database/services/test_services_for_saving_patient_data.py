from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO
from txmatching.data_transfer_objects.patients.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.services.patient_service import (
    save_patients_from_excel_to_empty_txm_event, update_donor,
    update_recipient)
from txmatching.database.sql_alchemy_schema import (
    AppUserModel, ConfigModel, DonorModel, PairingResultModel,
    RecipientAcceptableBloodModel, RecipientHLAAntibodyModel, RecipientModel)
from txmatching.patients.patient import RecipientRequirements
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntibody,
                                                    HLAType)
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


class TestSolveFromDbAndItsSupportFunctionality(DbTests):
    def test_saving_patients_from_obfuscated_excel(self):
        patients = parse_excel_data(get_absolute_path('tests/test_utilities/patient_data_2020_07_obfuscated.xlsx'))
        txm_event = create_or_overwrite_txm_event('test')
        save_patients_from_excel_to_empty_txm_event(patients, txm_event.db_id)

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
        self.assertEqual(4, len(app_users))

        self.assertEqual(650, len(list(solve_from_db(Configuration(), txm_event.db_id))))

    def test_saving_patients(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()

        self.assertSetEqual({'0', 'A'}, {blood.blood_type for blood in RecipientModel.query.get(1).acceptable_blood})
        self.assertSetEqual({'B7', 'DQ6', 'DQ5'},
                            {hla_antibody.code for hla_antibody in RecipientModel.query.get(1).hla_antibodies})
        self.assertFalse(
            RecipientModel.query.get(1).recipient_requirements['require_better_match_in_compatibility_index'])
        update_recipient(RecipientUpdateDTO(
            acceptable_blood_groups=['AB'],
            hla_antibodies=HLAAntibodies([HLAAntibody(mfi=20, cutoff=10, code='B43', raw_code='B43')]),
            recipient_requirements=RecipientRequirements(require_better_match_in_compatibility_index=True),
            db_id=1
        ), txm_event_db_id)

        self.assertSetEqual({'AB'}, {blood.blood_type for blood in RecipientModel.query.get(1).acceptable_blood})
        self.assertSetEqual({'B43'}, {code.code for code in RecipientModel.query.get(1).hla_antibodies})
        self.assertTrue(
            RecipientModel.query.get(1).recipient_requirements['require_better_match_in_compatibility_index'])

    def test_saving_donors(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()

        self.assertSetEqual({'A11',
                             'B8',
                             'DR11'},
                            {hla_type['code'] for hla_type in DonorModel.query.get(1).hla_typing['hla_types_list']})

        update_donor(DonorUpdateDTO(
            hla_typing=HLATypingDTO([HLAType('A11')]),
            db_id=1
        ), txm_event_db_id)

        self.assertSetEqual({'A11'},
                            {hla_type['code'] for hla_type in DonorModel.query.get(1).hla_typing['hla_types_list']})
