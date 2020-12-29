import json

import dacite
import dataclasses

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
    get_txm_event, save_patients_from_excel_to_txm_event, update_donor,
    update_recipient)
from txmatching.database.sql_alchemy_schema import (
    AppUserModel, ConfigModel, DonorModel, PairingResultModel,
    RecipientAcceptableBloodModel, RecipientHLAAntibodyModel, RecipientModel)
from txmatching.patients.patient import RecipientRequirements
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path
from txmatching.utils.logged_user import get_current_user_id


class TestUpdateDonorRecipient(DbTests):
    def test_saving_patients_from_obfuscated_excel(self):
        txm_event = create_or_overwrite_txm_event('test')
        patients = parse_excel_data(
            get_absolute_path('tests/resources/patient_data_2020_07_obfuscated_multi_country.xlsx'),
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

        save_patients_from_excel_to_txm_event(patients)

        configs = ConfigModel.query.all()
        recipients = RecipientModel.query.all()
        donors = DonorModel.query.all()
        pairing_results = PairingResultModel.query.all()
        recipient_acceptable_bloods = RecipientAcceptableBloodModel.query.all()
        recipient_hla_antibodies = RecipientHLAAntibodyModel.query.all()
        app_users = AppUserModel.query.all()

        txm_event = get_txm_event(txm_event.db_id)

        recipients_tuples = [(
            r.medical_id,
            r.parameters.country_code,
            r.parameters.blood_group,
            [a.code for a in r.hla_antibodies.hla_antibodies_list],
            [a.code for a in r.parameters.hla_typing.hla_types_list],
            r.acceptable_blood_groups
        )
            for r in txm_event.active_recipients_dict.values()]

        donors_tuples = [(
            r.medical_id,
            r.parameters.country_code,
            r.parameters.blood_group,
            [a.code for a in r.parameters.hla_typing.hla_types_list],
            txm_event.active_recipients_dict[r.related_recipient_db_id].medical_id if r.related_recipient_db_id else ""
        )
            for r in txm_event.active_donors_dict.values()]

        self.assertEqual(0, len(configs))
        self.assertEqual(34, len(recipients))
        self.assertEqual(38, len(donors))
        self.assertEqual(3, len({donor.country for donor in donors}))
        self.assertEqual(3, len({recipient.country for recipient in recipients}))
        self.assertEqual(0, len(pairing_results))
        self.assertEqual(91, len(recipient_acceptable_bloods))
        self.assertEqual(1059, len(recipient_hla_antibodies))
        self.assertEqual(6, len(app_users))

        all_matchings = list(solve_from_configuration(Configuration(
            max_cycle_length=100,
            max_sequence_length=100,
            max_number_of_distinct_countries_in_round=100),
            txm_event.db_id).calculated_matchings)

        self.assertCountEqual(['128A-IND-D', '148A-CZE-D', '133A-CZE-D', '126A-CAN-D', '158A-IND-D'],
                              [pair.donor.medical_id for pair in all_matchings[0].matching_pairs])

        self.assertCountEqual(['158A-IND-D', '133A-CZE-D', '128A-IND-D'],
                              [pair.donor.medical_id for pair in all_matchings[-1].matching_pairs])

        matching_tuples = [[(t.donor.medical_id, t.recipient.medical_id)
                            for t in res.get_donor_recipient_pairs()] for res in all_matchings]

        self.maxDiff = None
        # with open(get_absolute_path('tests/resources/recipients_tuples.json'), 'w') as f:
        #     json.dump(recipients_tuples, f)
        # with open(get_absolute_path('tests/resources/donors_tuples.json'), 'w') as f:
        #     json.dump(donors_tuples, f)
        # with open(get_absolute_path('tests/resources/patient_data_2020_07_obfuscated_multi_country.json'), 'w') as f:
        #     json.dump(matching_tuples, f)

        with open(get_absolute_path('tests/resources/recipients_tuples.json')) as f:
            expected_recipients_tuples = json.load(f)
        with open(get_absolute_path('tests/resources/donors_tuples.json')) as f:
            expected_donors_tuples = json.load(f)
        with open(get_absolute_path('tests/resources/patient_data_2020_07_obfuscated_multi_country.json')) as f:
            expected_matching_tuples = json.load(f)

        expected_recipients_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]),
                                       frozenset(tup[4]), frozenset(tup[5])
                                       ) for tup in expected_recipients_tuples]
        recipients_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]),
                              frozenset(tup[4]), frozenset(tup[5])
                              ) for tup in recipients_tuples]

        expected_donors_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]), tup[4]) for tup in
                                  expected_donors_tuples]
        donors_tuples = [(tup[0], tup[1], tup[2], frozenset(tup[3]), tup[4]) for tup in donors_tuples]

        expected_matching_tuples = {frozenset(tuple(tt) for tt in tup) for tup in expected_matching_tuples}

        for i, r in enumerate(recipients_tuples):
            self.assertTrue(r in expected_recipients_tuples, f"Error in round {i}: {r} not found")

        for i, d in enumerate(donors_tuples):
            self.assertTrue(d in expected_donors_tuples, f"Error in round {i}: {d} not found")

        for i, m in enumerate(matching_tuples):
            self.assertTrue(frozenset(m) in expected_matching_tuples, f"Error in round {i}: {m} not found")

        self.assertEqual(572, len(all_matchings))

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

    def test_update_donor_active(self):
        txm_event_db_id = self.fill_db_with_patients_and_results()
        donor_db_id = 1
        original_donor_model = DonorModel.query.get(donor_db_id)
        original_txm_event = get_txm_event(txm_event_db_id)
        self.assertEqual(True, original_donor_model.active)
        self.assertIn(original_donor_model.id, original_txm_event.active_donors_dict.keys())
        self.assertIn(original_donor_model.recipient_id, original_txm_event.active_recipients_dict.keys())

        update_donor(DonorUpdateDTO(
            active=False,
            db_id=donor_db_id
        ), txm_event_db_id)
        new_txm_event = get_txm_event(txm_event_db_id)

        self.assertEqual(False, DonorModel.query.get(donor_db_id).active)
        self.assertNotIn(donor_db_id, new_txm_event.active_donors_dict.keys())
        self.assertNotIn(original_donor_model.recipient_id, new_txm_event.active_recipients_dict.keys())
