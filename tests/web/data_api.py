import unittest

from txmatching.config.configuration import Configuration
from txmatching.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from txmatching.data_transfer_objects.configuration.configuration_from_dto import configuration_from_dto
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.web import create_app


class TestSaveAndGetConfiguration(unittest.TestCase):
    def test_get_config(self):
        app = create_app()
        with app.test_client() as client:
            with app.app_context():
                conf_dto = configuration_to_dto(Configuration(scorer_constructor_name="test"))

                client.post("/configuration", json=conf_dto)

                self.assertEqual("test", ConfigModel.query.get(0).parameters["scorer_constructor_name"])

                conf_request = client.get("/configuration")
                conf = configuration_from_dto(conf_request.json)
                self.assertEqual(Configuration(scorer_constructor_name="test"), conf)

                client.post("/configuration", json=configuration_to_dto(Configuration()))
