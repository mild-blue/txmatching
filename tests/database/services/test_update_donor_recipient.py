from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.data_transfer_objects.hla.parsing_error_dto import ParsingError
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import (
    HLAAntibodiesUpdateDTO, HLAAntibodyUpdateDTO)
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.hla_code_update_dtos import (
    HLATypeUpdateDTO, HLATypingUpdateDTO)
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.services.patient_service import (update_donor,
                                                          update_recipient)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.database.sql_alchemy_schema import (ConfigModel, DonorModel,
                                                    RecipientModel)
from txmatching.patients.patient import RecipientRequirements


class TestUpdateDonorRecipient(DbTests):

    def test_update_recipient(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        recipient_db_id = 1
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({'0', 'A'}, {blood.blood_type for blood in RecipientModel.query.get(recipient_db_id).acceptable_blood})
        self.assertSetEqual({'B7', 'DQ6', 'DQ5'},
                            {hla_antibody['code']['split'] for hla_antibody_group in
                             RecipientModel.query.get(recipient_db_id).hla_antibodies['hla_antibodies_per_groups'] for hla_antibody in
                             hla_antibody_group['hla_antibody_list']})
        self.assertFalse(
            RecipientModel.query.get(recipient_db_id).recipient_requirements['require_better_match_in_compatibility_index'])
        etag=RecipientModel.query.get(recipient_db_id).etag
        update_recipient(RecipientUpdateDTO(
            acceptable_blood_groups=['AB'],
            hla_antibodies=HLAAntibodiesUpdateDTO([HLAAntibodyUpdateDTO(mfi=20, raw_code='B42'),
                                                   HLAAntibodyUpdateDTO(mfi=20, raw_code='DQ[01:03,      06:03]')
                                                   ]),
            hla_typing=HLATypingUpdateDTO([
                HLATypeUpdateDTO('A11'),
                HLATypeUpdateDTO('DQ[01:03,      06:03]')
            ]),
            recipient_requirements=RecipientRequirements(require_better_match_in_compatibility_index=True),
            db_id=recipient_db_id,
            etag=etag
        ), txm_event_db_id)

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({'AB'}, {blood.blood_type for blood in RecipientModel.query.get(recipient_db_id).acceptable_blood})
        self.assertSetEqual({None, 'DQB1*06:03', 'DQA1*01:03'},
                            {hla_antibody['code']['high_res'] for hla_antibody_group in
                             RecipientModel.query.get(recipient_db_id).hla_antibodies['hla_antibodies_per_groups'] for hla_antibody in
                             hla_antibody_group['hla_antibody_list']})
        self.assertTrue(
            RecipientModel.query.get(recipient_db_id).recipient_requirements['require_better_match_in_compatibility_index'])
        self.assertSetEqual({None, 'DQB1*06:03', 'DQA1*01:03'},
                            {hla_type['code']['high_res'] for hla_group in
                             RecipientModel.query.get(recipient_db_id).hla_typing['hla_per_groups'] for hla_type in
                             hla_group['hla_types']})

    def test_update_recipient_cutoff(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        new_cutoff = 8000
        recipient_db_id = 1
        self.assertSetEqual({2000},
                            {hla_antibody.cutoff for hla_antibody in RecipientModel.query.get(1).hla_antibodies_raw})
        etag = RecipientModel.query.get(recipient_db_id).etag
        update_recipient(RecipientUpdateDTO(
            cutoff=new_cutoff,
            db_id=recipient_db_id,
            etag=etag
        ), txm_event_db_id)
        self.assertEqual(new_cutoff, RecipientModel.query.get(recipient_db_id).recipient_cutoff)
        self.assertSetEqual({new_cutoff}, {code.cutoff for code in RecipientModel.query.get(recipient_db_id).hla_antibodies_raw})

    def test_update_donor(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        donor_db_id = 1
        etag = DonorModel.query.get(donor_db_id).etag
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({'A11',
                             'B8',
                             'DR11'},
                            {hla_type['code']['split']
                             for hla_group in DonorModel.query.get(donor_db_id).hla_typing['hla_per_groups'] for hla_type in
                             hla_group['hla_types']})

        update_donor(DonorUpdateDTO(
            hla_typing=HLATypingUpdateDTO([
                HLATypeUpdateDTO('A11'),
                HLATypeUpdateDTO('DQ[01:03,      06:03]')
            ]),
            db_id=donor_db_id,
            etag=etag
        ), txm_event_db_id)

        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).all()
        self.assertEqual(1, len(configs))

        self.assertSetEqual({None, 'DQB1*06:03', 'DQA1*01:03'},
                            {hla_type['code']['high_res'] for hla_group in
                             DonorModel.query.get(1).hla_typing['hla_per_groups'] for hla_type in
                             hla_group['hla_types']})

    def test_update_donor_active(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        donor_db_id = 1
        original_donor_model = DonorModel.query.get(donor_db_id)
        original_txm_event = get_txm_event_complete(txm_event_db_id)
        self.assertEqual(True, original_donor_model.active)
        self.assertIn(original_donor_model.id, original_txm_event.active_and_valid_donors_dict.keys())
        self.assertIn(original_donor_model.recipient_id, original_txm_event.active_and_valid_recipients_dict.keys())
        etag = DonorModel.query.get(donor_db_id).etag
        update_donor(DonorUpdateDTO(
            active=False,
            db_id=donor_db_id,
            etag=etag
        ), txm_event_db_id)
        new_txm_event = get_txm_event_complete(txm_event_db_id)

        self.assertEqual(False, DonorModel.query.get(donor_db_id).active)
        self.assertNotIn(donor_db_id, new_txm_event.active_and_valid_donors_dict.keys())
        self.assertNotIn(original_donor_model.recipient_id, new_txm_event.active_and_valid_recipients_dict.keys())
