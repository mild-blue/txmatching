from collections import namedtuple
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import patch

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, Recipient, TxmEvent
from txmatching.patients.recipient_compatibility import \
    calculate_cpra_and_get_compatible_donors_for_recipient
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import HLACrossmatchLevel
from txmatching.utils.hla_system.hla_preparation_utils import (
    create_antibodies, create_antibody, create_hla_typing)


class TestCPRACalculation(TestCase):

    def setUp(self) -> None:
        self.some_hla_raw_codes = ['A*24:09N', 'A*32:02', 'B*57:16', 'A*02:140', 'A10', 'DR4',
                                   'DRB1*04:10', 'B*44:55', 'DQB1*06:01', 'A*02:08', 'A*02:140',
                                   'DPA1*01:18', 'A32']

        self.recipient_hla_raw_codes = ['A32', 'B57', 'A2']

        # creating recipients for different solutions
        self.recipient_general = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[create_antibody(
                raw_code=self.some_hla_raw_codes[1],  # recipient just with A*32:02 antibody
                mfi=4000,
                cutoff=2000)]
            ),
            create_hla_typing(self.recipient_hla_raw_codes)
        )
        self.recipient_without_antibodies = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[]), 
            create_hla_typing(self.recipient_hla_raw_codes)
        )
        self.recipient_against_all_donors = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[create_antibody(
                raw_code=raw_code,  # recipient has antibodies against all donors in txm_event
                mfi=4000,
                cutoff=2000)
                for raw_code in self.some_hla_raw_codes]
            ),
            create_hla_typing(self.recipient_hla_raw_codes)
        )

        self.PatientsTuple = namedtuple(
            typename='patients',
            field_names=['recipients', 'donors']
        )

        # create donors for general txm_event
        donors = []
        for i in range(len(self.some_hla_raw_codes) - 1):
            donors.append(self.__create_mock_donor_object_with_hla_typing(
                create_hla_typing([self.some_hla_raw_codes[i], self.some_hla_raw_codes[i + 1]]),
                i + 1
            ))

        # creating general txm_event with mock
        self.txm_event_general = self.__create_mock_txm_event_object_with_patients(
            self.PatientsTuple(
                recipients=[self.recipient_general, self.recipient_without_antibodies],
                donors=donors
            )
        )

        # creating general config parameters:
        # The tests DO NOT CONTROL the dependence of cPRA and compatible_donors on CONFIGURATION!
        # If you have changed crossmatch logic (function is_positive_hla_crossmatch()) for some config 
        # or scorer's config parameters, the expected results should be recalculated!
        self.config_parameters_general = ConfigParameters(use_high_resolution=True,
                                                         hla_crossmatch_level=HLACrossmatchLevel.BROAD)

    def test_calculate_cpra_for_recipient_general_case(self):
        """Case: usual recipient in standard conditions"""

        recipient_donors_compatibility = calculate_cpra_and_get_compatible_donors_for_recipient(
            txm_event=self.txm_event_general, recipient=self.recipient_general, 
            configuration_parameters=self.config_parameters_general, compute_cpra=True)

        self.assertEqual(
            (0.25, {3, 4, 9, 10, 11}),
            (recipient_donors_compatibility.cpra, recipient_donors_compatibility.compatible_donors))

    def test_calculate_cpra_for_recipient_without_antibodies_case(self):
        """Case: recipient without antibodies"""

        recipient_donors_compatibility = calculate_cpra_and_get_compatible_donors_for_recipient(
            txm_event=self.txm_event_general, recipient=self.recipient_without_antibodies, 
            configuration_parameters=self.config_parameters_general, compute_cpra=True)

        self.assertEqual(
            (0, {1, 2, 3, 4, 9, 10, 11, 12}),
            (recipient_donors_compatibility.cpra, recipient_donors_compatibility.compatible_donors))

    def test_calculate_cpra_for_recipient_against_all_donors_case(self):
        """Case: recipient is incompatible to all donors in txm_event"""

        recipient_donors_compatibility = calculate_cpra_and_get_compatible_donors_for_recipient(
            txm_event=self.txm_event_general, recipient=self.recipient_against_all_donors, 
            configuration_parameters=self.config_parameters_general, compute_cpra=True)

        self.assertEqual(
            (1, set()),
            (recipient_donors_compatibility.cpra, recipient_donors_compatibility.compatible_donors))

    def test_calculate_cpra_for_recipient_no_donors_case(self):
        """Case: txm_event without donors for usual recipient"""
        txm_event = self.__create_mock_txm_event_object_with_patients(
            self.PatientsTuple(donors=[],
                               recipients=[self.recipient_general]))

        recipient_donors_compatibility = calculate_cpra_and_get_compatible_donors_for_recipient(
            txm_event=txm_event, recipient=self.recipient_against_all_donors, 
            configuration_parameters=self.config_parameters_general, compute_cpra=True)

        self.assertEqual(
            (1, set()),
            (recipient_donors_compatibility.cpra, recipient_donors_compatibility.compatible_donors))

    @staticmethod
    @patch(f'{__name__}.Recipient')
    def __create_mock_recipient_object_with_hla_antibodies(hla_antibodies, hla_typing, mocked_Recipient):
        recipient = mocked_Recipient.return_value
        recipient.hla_antibodies = hla_antibodies
        recipient.parameters.hla_typing = hla_typing
        recipient.parameters.blood_group = BloodGroup.A
        return recipient

    @staticmethod
    @patch(f'{__name__}.Donor')
    def __create_mock_donor_object_with_hla_typing(hla_typing, db_id, mocked_Donor):
        donor = mocked_Donor.return_value
        donor.parameters.hla_typing = hla_typing
        donor.parameters.blood_group = BloodGroup.A
        donor.db_id = db_id
        return donor

    @staticmethod
    @patch(f'{__name__}.TxmEvent')
    def __create_mock_txm_event_object_with_patients(patients: Tuple[List[int]], mocked_TxmEvent):
        txm_event = mocked_TxmEvent.return_value
        txm_event.all_recipients = patients.recipients
        txm_event.active_and_valid_donors_dict = {donor.db_id: donor for donor in patients.donors}
        return txm_event
