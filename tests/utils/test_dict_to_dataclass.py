from enum import Enum
import time

import dacite
from yoyo import logger

from txmatching.data_transfer_objects.patients.hla_antibodies_dto import HLAAntibodiesDTO
from txmatching.patients.hla_code import HLACode
from txmatching.patients.hla_model import AntibodiesPerGroup, HLAAntibody
from txmatching.utils.enums import HLAGroup
from tests.test_utilities.prepare_app_for_tests import DbTests

class TestDictToDataclass(DbTests):
    def test_dict_to_dataclass(self):
        data = {
                "hla_antibodies_per_groups": [
                    {
                        "hla_group": "A",
                        "hla_antibody_list": []
                    },
                    {
                        "hla_group": "B",
                        "hla_antibody_list": []
                    },
                    {
                        "hla_group": "DRB1",
                        "hla_antibody_list": []
                    },
                    {
                        "hla_group": "Other",
                        "hla_antibody_list": [
                            {
                                "mfi": 8000,
                                "code": {
                                    "broad": "DQ2",
                                    "group": "DQB",
                                    "split": "DQ2",
                                    "high_res": None
                                },
                                "cutoff": 2000,
                                "raw_code": "DQ2"
                            },
                            {
                                "mfi": 8000,
                                "code": {
                                    "broad": "DQ4",
                                    "group": "DQB",
                                    "split": "DQ4",
                                    "high_res": None
                                },
                                "cutoff": 2000,
                                "raw_code": "DQ4"
                            },
                            {
                                "mfi": 8000,
                                "code": {
                                    "broad": "DQ3",
                                    "group": "DQB",
                                    "split": "DQ7",
                                    "high_res": None
                                },
                                "cutoff": 2000,
                                "raw_code": "DQ7"
                            },
                            {
                                "mfi": 8000,
                                "code": {
                                    "broad": "DQ3",
                                    "group": "DQB",
                                    "split": "DQ8",
                                    "high_res": None
                                },
                                "cutoff": 2000,
                                "raw_code": "DQ8"
                            },
                            {
                                "mfi": 8000,
                                "code": {
                                    "broad": "DQ3",
                                    "group": "DQB",
                                    "split": "DQ9",
                                    "high_res": None
                                },
                                "cutoff": 2000,
                                "raw_code": "DQ9"
                            }
                        ]
                    }
                ]
            }

        start_time = time.time()

        antibodies_dto_dacite: HLAAntibodiesDTO = dacite.from_dict(
            data_class=HLAAntibodiesDTO, data=data,
            config=dacite.Config(cast=[Enum])
        )

        dacite_end_time = time.time()

        antibodies_dto_list_comprehension = HLAAntibodiesDTO([
                                AntibodiesPerGroup(hla_group=hla["hla_group"],
                                                   hla_antibody_list=[HLAAntibody(
                                                    raw_code=antibody['raw_code'],
                                                    mfi=antibody["mfi"],
                                                    cutoff=antibody["cutoff"],
                                                    code=HLACode(high_res=antibody["code"]["high_res"],
                                                                split=antibody["code"]["split"],
                                                                broad=antibody["code"]["broad"],
                                                                group=HLAGroup(antibody["code"]["group"]))
                                                   ) for antibody in hla["hla_antibody_list"]])
                                for hla in data['hla_antibodies_per_groups']])
        
        dataclass_end_time = time.time()

        dacite_time = dacite_end_time - start_time
        dataclass_time = dataclass_end_time - dacite_end_time

        self.assertGreater(dacite_time, 3 * dataclass_time)
        self.assertEqual(antibodies_dto_dacite, antibodies_dto_list_comprehension)

        logger.info(f"Dacite time: {dacite_time}, Dataclass time: {dataclass_time}")
