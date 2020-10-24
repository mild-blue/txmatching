import dataclasses
import logging
from typing import Dict, Optional

from dacite import Config, from_dict

from txmatching.configuration.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ConfigModel
from txmatching.utils.enums import Country
from txmatching.utils.logged_user import get_current_user_id

logger = logging.getLogger(__name__)


def configuration_from_dict(config_model: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_model,
                              config=Config(cast=[Country]))
    return configuration


def get_configuration_for_txm_event(txm_event_db_id: int) -> Configuration:
    current_config_model = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).first()
    if current_config_model is None:
        return Configuration()
    else:
        return configuration_from_dict(current_config_model.parameters)


def save_configuration_to_db(configuration: Configuration, txm_event_db_id: int) -> int:
    config_model = _configuration_to_config_model(configuration, txm_event_db_id)
    previous_config = get_config_model_for_txm_event(txm_event_db_id)
    if previous_config:
        db.session.delete(previous_config)
        db.session.flush()

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def get_config_model_for_txm_event(txm_event_db_id: int) -> Optional[ConfigModel]:
    config = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event_db_id).first()
    return config


def _configuration_to_config_model(configuration: Configuration, txm_event_db_id: int) -> ConfigModel:
    user_id = get_current_user_id()
    return ConfigModel(parameters=dataclasses.asdict(configuration), created_by=user_id, txm_event_id=txm_event_db_id)
