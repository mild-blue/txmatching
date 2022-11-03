from collections import namedtuple
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import patch

from tests.test_utilities.hla_preparation_utils import (create_antibodies,
                                                        create_antibody,
                                                        create_hla_typing)
from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import (
    Donor, Recipient, TxmEvent,
    calculate_cpra_and_get_compatible_donors_for_recipient)
from txmatching.utils.enums import HLACrossmatchLevel


class TestCPRACalculation(TestCase):

    def setUp(self) -> None:
        self.some_hla_raw_codes = ['A*24:09N', 'A*32:02', 'B*57:16', 'A*02:140', 'A10', 'DR4',
                                   'DRB1*04:10', 'B*44:55', 'DQB1*06:01', 'A*02:08', 'A*02:140',
                                   'DPA1*01:18', 'A32']

        # creating recipients for different solutions
        self.recipient_general = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[create_antibody(
                raw_code=self.some_hla_raw_codes[1],  # recipient just with A*32:02 antibody
                mfi=4000,
                cutoff=2000)]
            )
        )
        self.recipient_without_antibodies = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[])
        )
        self.recipient_against_all_donors = self.__create_mock_recipient_object_with_hla_antibodies(
            create_antibodies(hla_antibodies_list=[create_antibody(
                raw_code=raw_code,  # recipient has antibodies against all donors in txm_event
                mfi=4000,
                cutoff=2000)
                for raw_code in self.some_hla_raw_codes]
            )
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
        # The tests DO NOT CONTROL the dependence of cPRA on CONFIGURATION!
        # If you have changed crossmatch logic (function is_positive_hla_crossmatch()) for some config,
        # the expected results should be recalculated!
        self.config_parameters_general = ConfigParameters(use_high_resolution=True,
                                                          hla_crossmatch_level=HLACrossmatchLevel.BROAD)

    def test_calculate_cpra_for_recipient_general_case(self):
        """Case: usual recipient in standard conditions"""
        self.assertEqual(
            (0.25, {3, 4, 5, 6, 7, 8, 9, 10, 11}),
            calculate_cpra_and_get_compatible_donors_for_recipient(txm_event=self.txm_event_general,
                                                                   recipient=self.recipient_general,
                                                                   config_parameters=self.config_parameters_general))

    def test_calculate_cpra_for_recipient_without_antibodies_case(self):
        """Case: recipient without antibodies"""
        self.assertEqual(
            (0, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}),
            calculate_cpra_and_get_compatible_donors_for_recipient(txm_event=self.txm_event_general,
                                                                   recipient=self.recipient_without_antibodies,
                                                                   config_parameters=self.config_parameters_general))

    def test_calculate_cpra_for_recipient_against_all_donors_case(self):
        """Case: recipient is incompatible to all donors in txm_event"""
        self.assertEqual(
            (1, set()),
            calculate_cpra_and_get_compatible_donors_for_recipient(txm_event=self.txm_event_general,
                                                                   recipient=self.recipient_against_all_donors,
                                                                   config_parameters=self.config_parameters_general))

    def test_calculate_cpra_for_recipient_no_donors_case(self):
        """Case: txm_event without donors for usual recipient"""
        txm_event = self.__create_mock_txm_event_object_with_patients(
            self.PatientsTuple(donors=[],
                               recipients=[self.recipient_general]))
        self.assertEqual(
            (1, set()),
            calculate_cpra_and_get_compatible_donors_for_recipient(txm_event=txm_event,
                                                                   recipient=self.recipient_general,
                                                                   config_parameters=self.config_parameters_general))

    @staticmethod
    @patch(f'{__name__}.Recipient')
    def __create_mock_recipient_object_with_hla_antibodies(hla_antibodies, mocked_Recipient):
        recipient = mocked_Recipient.return_value
        recipient.hla_antibodies = hla_antibodies
        return recipient

    @staticmethod
    @patch(f'{__name__}.Donor')
    def __create_mock_donor_object_with_hla_typing(hla_typing, db_id, mocked_Donor):
        donor = mocked_Donor.return_value
        donor.parameters.hla_typing = hla_typing
        donor.db_id = db_id
        return donor

    @staticmethod
    @patch(f'{__name__}.TxmEvent')
    def __create_mock_txm_event_object_with_patients(patients: Tuple[List[int]], mocked_TxmEvent):
        txm_event = mocked_TxmEvent.return_value
        txm_event.all_recipients = patients.recipients
        txm_event.active_and_valid_donors_dict = {donor.db_id: donor for donor in patients.donors}
        return txm_event
