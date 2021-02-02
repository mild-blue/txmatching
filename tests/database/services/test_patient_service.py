import hashlib

from tests.test_utilities.create_dataclasses import (get_test_donors,
                                                     get_test_recipients)
from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.data_transfer_objects.patients.upload_dto.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dto.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.db import db
from txmatching.database.services.patient_service import (_update_hash,
                                                          get_patients_hash)
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.patients.hla_model import HLAType
from txmatching.patients.patient import DonorType, TxmEvent
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.enums import Country, Sex
from txmatching.utils.logged_user import get_current_user_id

TXM_EVENT_NAME = 'test'

DONOR_UPLOAD_DTOS = [
    DonorUploadDTO(
        medical_id='D1',
        blood_group=BloodGroup.A,
        hla_typing=[
            'A9', 'A21'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R1',
        sex=Sex.M,
        height=180,
        weight=90,
        year_of_birth=1965
    ),
    DonorUploadDTO(
        medical_id='D2',
        blood_group=BloodGroup.B,
        hla_typing=[
            'A9', 'A21'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R2',
        sex=Sex.M,
        height=178,
        weight=69,
        year_of_birth=1967
    ),
    DonorUploadDTO(
        medical_id='D3',
        blood_group=BloodGroup.AB,
        hla_typing=[
            'A9'
        ],
        donor_type=DonorType.DONOR.value,
        related_recipient_medical_id='R3',
        sex=Sex.M,
        height=145,
        weight=56,
        year_of_birth=1989
    ),
]

RECIPIENT_UPLOAD_DTOS = [
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.A,
            BloodGroup.ZERO
        ],
        medical_id='R1',
        blood_group=BloodGroup.A,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2100
            )
        ],
        sex=Sex.F,
        height=150,
        weight=65,
        year_of_birth=2001,
        waiting_since='2020-01-06',
        previous_transplants=0
    ),
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.B,
            BloodGroup.ZERO
        ],
        medical_id='R2',
        blood_group=BloodGroup.B,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2200
            )
        ],
        sex=Sex.F,
        height=189,
        weight=70,
        year_of_birth=1996,
        waiting_since='2020-02-07',
        previous_transplants=0
    ),
    RecipientUploadDTO(
        acceptable_blood_groups=[
            BloodGroup.ZERO
        ],
        medical_id='R3',
        blood_group=BloodGroup.ZERO,
        hla_typing=[
            'A9', 'A21'
        ],
        hla_antibodies=[
            HLAAntibodiesUploadDTO(
                name='B42',
                mfi=2000,
                cutoff=2300
            )
        ],
        sex=Sex.M,
        height=201,
        weight=120,
        year_of_birth=1999,
        waiting_since='2020-05-13',
        previous_transplants=0
    )
]

PATIENT_UPLOAD_DTO = PatientUploadDTOIn(
    country=Country.CZE,
    txm_event_name=TXM_EVENT_NAME,
    donors=DONOR_UPLOAD_DTOS,
    recipients=RECIPIENT_UPLOAD_DTOS
)


class TestPatientService(DbTests):

    def test_update_txm_event_patients(self):
        txm_event = create_or_overwrite_txm_event(name=TXM_EVENT_NAME)

        # Insert config and validates that it is stored into DB
        user_id = get_current_user_id()
        config = ConfigModel(  # TODOO
            txm_event_id=txm_event.db_id,
            parameters={},
            patients_hash=get_patients_hash(txm_event),
            created_by=user_id
        )

        db.session.add(config)
        db.session.commit()
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(1, len(configs))

        replace_or_add_patients_from_one_country(PATIENT_UPLOAD_DTO)

        # Validate that configs of particular TXM event are not deleted.
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(1, len(configs))

        # Validate that patients hash has changed
        self.assertNotEqual(config.patients_hash)

    def test_hashing(self):
        def _assert_hash(value, expected_hash_digest):
            hash_ = hashlib.md5()
            _update_hash(hash_, value)
            #print(hash_.hexdigest())  # TODOO
            #return
            self.assertEqual(hash_.hexdigest(), expected_hash_digest)

        _assert_hash('foo', '56c527b4cc0b522b127062dec3201194')
        _assert_hash('42', 'aa0a056d9e7d1b3b17530b46107b91a3')
        _assert_hash(42, 'd1e2cf72d8bf073f0bc2d0e8794b31ae')
        _assert_hash(42.0, 'ee8b51ea1d5859dc45035c4ee9fcaedc')
        _assert_hash(True, '3b3e200b7cda75063ec203db706d2463')
        _assert_hash([42], '7c4aa0d7ffabc559d31ae902ae2b93a6')
        _assert_hash([1, 2], '50d69227171683e044fc85f530d31568')
        _assert_hash({1, 2}, '26b3a59f9692f43f20db24e6ab242cb7')
        _assert_hash((1, True), 'e70e4791e78da2db05688c6043a20d86')
        _assert_hash({'a': 'b'}, 'e4625008dde72175d331df31f62572e9')
        _assert_hash(None, '6af5817033462a81dfdff478e27e824d')
        _assert_hash(get_test_donors(), 'e799dd070b8c420c7b9c026969dbf663')
        _assert_hash(get_test_recipients(), '344d1610eab01d736c40b1938492515a')

    def test_get_patients_hash(self):
        txm_event_1 = TxmEvent(
            1, 'event_name_1',
            all_donors=get_test_donors(),
            all_recipients=get_test_recipients(),
            active_donors_dict=None, active_recipients_dict=None
        )
        hash_1 = get_patients_hash(txm_event_1)

        # changing event db id, event name does not change the hash
        txm_event_2 = TxmEvent(
            2, 'event_name_2',
            all_donors=get_test_donors(),
            all_recipients=get_test_recipients(),
            active_donors_dict=None, active_recipients_dict=None
        )
        hash_2 = get_patients_hash(txm_event_2)
        self.assertEqual(hash_1, hash_2)

        # Changing donors changes the hash
        txm_event_3 = TxmEvent(
            1, 'event_name_1',
            all_donors=[],
            all_recipients=get_test_recipients(),
            active_donors_dict=None, active_recipients_dict=None
        )
        hash_3 = get_patients_hash(txm_event_3)
        self.assertNotEqual(hash_1, hash_3)

        # Changing recipients changes the hash
        txm_event_4 = TxmEvent(
            1, 'event_name_1',
            all_donors=get_test_donors(),
            all_recipients=[],
            active_donors_dict=None, active_recipients_dict=None
        )
        hash_4 = get_patients_hash(txm_event_4)
        self.assertNotEqual(hash_1, hash_4)

        # changing hla type changes the hash
        new_donors = get_test_donors()
        self.assertEqual(
            new_donors[0].parameters.hla_typing.hla_per_groups[0].hla_types[0],
            HLAType('A1')
        )
        new_donors[0].parameters.hla_typing.hla_per_groups[0].hla_types[0] = HLAType('A3')

        txm_event_5 = TxmEvent(
            1, 'event_name_1',
            all_donors=new_donors,
            all_recipients=get_test_recipients(),
            active_donors_dict=None, active_recipients_dict=None
        )
        hash_5 = get_patients_hash(txm_event_5)
        self.assertNotEqual(hash_1, hash_5)
