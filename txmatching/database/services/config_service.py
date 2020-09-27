import dataclasses
import logging
from typing import Dict, Iterator

from dacite import Config, from_dict
from sqlalchemy import and_

from txmatching.configuration.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.services import txm_event_service
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.utils.enums import Country
from txmatching.utils.logged_user import get_current_user_id

logger = logging.getLogger(__name__)


def configuration_from_dict(config_model: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_model,
                              config=Config(cast=[Country]))
    return configuration


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
    txm_event_db_id = txm_event_service.get_newest_txm_event_db_id()
    config_model = _configuration_to_config_model(configuration, txm_event_db_id)
    # explicitly saving as 0 -> default configuration
    config_model.id = 0
    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def _save_configuration_to_db(configuration: Configuration, txm_event_db_id: int) -> int:
    config_model = _configuration_to_config_model(configuration, txm_event_db_id)
    for existing_config in get_config_models(txm_event_db_id):
        if existing_config.parameters == config_model.parameters:
            return existing_config.id

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def get_config_models(txm_event_db_id: int) -> Iterator[ConfigModel]:
    configs = ConfigModel.query.filter(and_(ConfigModel.id > 0, ConfigModel.txm_event_id == txm_event_db_id)).all()
    return configs


def _configuration_to_config_model(configuration: Configuration, txm_event_db_id: int) -> ConfigModel:
    user_id = get_current_user_id()
    return ConfigModel(parameters=dataclasses.asdict(configuration), created_by=user_id, txm_event_id=txm_event_db_id)
