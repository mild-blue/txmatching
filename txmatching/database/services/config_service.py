import dataclasses
import logging
from typing import Dict, Iterator

from dacite import Config, from_dict

from txmatching.config.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.services import tx_session_service
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.utils.country import Country
from txmatching.utils.logged_user import get_current_user_id

logger = logging.getLogger(__name__)


def configuration_from_dict(config_model: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_model,
                              config=Config(cast=[Country]))
    return configuration


def get_configurations() -> Iterator[Configuration]:
    for config_model in get_config_models():
        yield configuration_from_dict(config_model.parameters)


def get_current_configuration() -> Configuration:
    current_config_model = ConfigModel.query.get(0)
    if current_config_model is None:
        save_configuration_as_current(Configuration())
        return Configuration()
    else:
        return configuration_from_dict(current_config_model.parameters)


def save_configuration_as_current(configuration: Configuration) -> int:
    maybe_config = ConfigModel.query.get(0)
    if maybe_config is not None:
        db.session.delete(maybe_config)
    tx_session = tx_session_service.get_newest_tx_session()
    config_model = _configuration_to_config_model(configuration, tx_session.id)
    # explicitly saving as 0 -> default configuration
    config_model.id = 0
    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def save_configuration_to_db(configuration: Configuration, tx_session_db_id: int) -> int:
    config_model = _configuration_to_config_model(configuration, tx_session_db_id)
    for existing_config in get_config_models():
        if existing_config.parameters == config_model.parameters:
            return existing_config.id

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def get_config_models() -> Iterator[ConfigModel]:
    configs = ConfigModel.query.filter(ConfigModel.id > 0).all()
    return configs


def _configuration_to_config_model(configuration: Configuration, tx_session_db_id: int) -> ConfigModel:
    user_id = get_current_user_id()
    return ConfigModel(parameters=dataclasses.asdict(configuration), created_by=user_id, tx_session_id=tx_session_db_id)
