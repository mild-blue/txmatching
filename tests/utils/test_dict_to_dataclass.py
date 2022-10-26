import time
from enum import Enum

import dacite
from yoyo import logger

from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.data_transfer_objects.patients.hla_antibodies_dto import \
    HLAAntibodiesDTO
from txmatching.database.services.patient_service import \
    _recipient_model_to_antibodies_dto
from txmatching.database.sql_alchemy_schema import RecipientModel


class TestDictToDataclass(DbTests):
    def test_dict_to_dataclass(self):
        txm_event_id = self.fill_db_with_patients()
        recipient_model = RecipientModel.query.filter_by(txm_event_id=txm_event_id).first()

        start_time = time.time()

        antibodies_dto_dacite: HLAAntibodiesDTO = dacite.from_dict(
            data_class=HLAAntibodiesDTO, data=recipient_model.hla_antibodies,
            config=dacite.Config(cast=[Enum])
        )

        dacite_end_time = time.time()

        antibodies_dto_list_comprehension = _recipient_model_to_antibodies_dto(recipient_model)

        dataclass_end_time = time.time()

        dacite_time = dacite_end_time - start_time
        dataclass_time = dataclass_end_time - dacite_end_time

        self.assertGreater(dacite_time, 3 * dataclass_time)
        self.assertEqual(antibodies_dto_dacite, antibodies_dto_list_comprehension)

        logger.info(f"Dacite time: {dacite_time}, Dataclass time: {dataclass_time}")
