import dataclasses

from tests.test_utilities.prepare_app import DbTests
from txmatching.config.configuration import Configuration
from txmatching.data_transfer_objects.configuration.configuration_from_dto import configuration_from_dto
from txmatching.data_transfer_objects.configuration.configuration_to_dto import configuration_to_dto
from txmatching.database.services.config_service import \
    save_configuration_as_current, get_current_configuration
from txmatching.utils.country import Country


class TestConfiguration(DbTests):
    def test_configuration(self):
        self.fill_db_with_patients_and_results()
        save_configuration_as_current(
            Configuration(forbidden_country_combinations=[(Country.CZE, Country.AUT)])
        )
        configuration = get_current_configuration()
        self.assertEqual(Country.CZE, configuration.forbidden_country_combinations[0][0])

    def test_configuration_from_dto(self):
        self.fill_db_with_patients_and_results()
        dto = configuration_to_dto(Configuration())

        dto_dict = dataclasses.asdict(dto)
        config = configuration_from_dto(dto_dict)

        self.assertEqual(Country.AUT, config.forbidden_country_combinations[0][0])
        self.assertEqual(Country.AUT, dto.forbidden_country_combinations[0][0])
