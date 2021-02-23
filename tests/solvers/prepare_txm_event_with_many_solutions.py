from tests.test_utilities.populate_db import (PATIENT_DATA_OBFUSCATED,
                                              create_or_overwrite_txm_event)
from tests.test_utilities.prepare_app import DbTests
from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import \
    DonorRecipientPairDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.patient_upload_service import (
    add_donor_recipient_pair, replace_or_add_patients_from_excel)
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.patients.patient import DonorType
from txmatching.solve_service.solve_from_configuration import \
    solve_from_configuration
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data
from txmatching.utils.get_absolute_path import get_absolute_path


def prepare_txm_event_with_many_solutions():
    txm_event = create_or_overwrite_txm_event('test')
    patients = parse_excel_data(get_absolute_path('/tests/resources/data2.xlsx'), txm_event.name, None)
    replace_or_add_patients_from_excel(patients)
    patients = parse_excel_data(get_absolute_path(PATIENT_DATA_OBFUSCATED), txm_event.name, None)
    replace_or_add_patients_from_excel(patients)
    add_donor_recipient_pair(
        DonorRecipientPairDTO(
            donor=DonorUploadDTO(donor_type=DonorType.DONOR, medical_id='t2', blood_group=BloodGroup.AB,
                                 related_recipient_medical_id=None, hla_typing=[]),
            recipient=RecipientUploadDTO(medical_id='t2', blood_group=BloodGroup.AB, hla_typing=[],
                                         acceptable_blood_groups=[], hla_antibodies=[]),
            country_code=Country.CZE
        ),
        txm_event.db_id
    )
    add_donor_recipient_pair(
        DonorRecipientPairDTO(
            donor=DonorUploadDTO(donor_type=DonorType.DONOR, medical_id='t1', blood_group=BloodGroup.AB,
                                 related_recipient_medical_id=None, hla_typing=[]),
            recipient=RecipientUploadDTO(medical_id='t1', blood_group=BloodGroup.AB, hla_typing=[],
                                         acceptable_blood_groups=[], hla_antibodies=[]),
            country_code=Country.CZE
        ),
        txm_event.db_id
    )

    txm_event = get_txm_event_complete(txm_event.db_id)

    return txm_event
