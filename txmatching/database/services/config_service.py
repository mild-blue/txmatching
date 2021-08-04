import dataclasses
import logging
from typing import Dict, Optional

from dacite import Config, from_dict

from txmatching.configuration.configuration import Configuration
from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import ConfigModel, TxmEventModel
from txmatching.patients.patient import TxmEvent
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLACrossmatchLevel

logger = logging.getLogger(__name__)


def configuration_from_config_model(config_model: ConfigModel) -> Configuration:
    return configuration_from_dict(config_model.parameters)


def configuration_from_dict(config_dict: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_dict,
                              config=Config(cast=[Country, HLACrossmatchLevel]))
    return configuration


def save_configuration_to_db(configuration: Configuration, txm_event_id: int, user_id: int) -> int:
    config_model = _configuration_to_config_model(configuration, txm_event_id, user_id)

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def set_config_as_default(txm_event_id: int, configuration_db_id: Optional[int]):
    TxmEventModel.query.filter(TxmEventModel.id == txm_event_id).update(
        {'default_config_id': configuration_db_id}
    )
    db.session.commit()


def _configuration_to_config_model(
        configuration: Configuration,
        txm_event_db_id: int,
        user_id: int
) -> ConfigModel:
    return ConfigModel(
        parameters=dataclasses.asdict(configuration),
        txm_event_id=txm_event_db_id,
        created_by=user_id
    )


def get_configuration_from_db_id(configuration_db_id: int, txm_event_id: int) -> Configuration:
    config_model = ConfigModel.query.get(configuration_db_id)
    if config_model is None:
        # As txm_event.default_config_id column is integer and not linked to config.id
        # (see comment in sql_alchemy_schema), it can happen that default_config_id is set while corresponding config
        # is deleted. Such problem happens in TestSwaggerEndpoint. For this reason, we handle it by returning default
        # configuration instance.
        logger.error(f'Configuration not found for db id {configuration_db_id}. Returning default configuration.')
        return Configuration()
    if txm_event_id != config_model.txm_event_id:
        logger.error(f'Configuration with db id {configuration_db_id} does '
                     f'not belong to txm event {txm_event_id}. Returning default configuration')
        return Configuration()

    return configuration_from_config_model(config_model)


def get_configuration_from_db_id_or_default(txm_event: TxmEvent, configuration_db_id: Optional[int]) -> Configuration:
    """
    Return configuration and does not check patient hash.
    - if specified, return configuration by configuration_db_id
    - otherwise, if specified, return default configuration of txm event
    - otherwise, return default Configuration() object
    """
    if configuration_db_id is not None:
        return get_configuration_from_db_id(configuration_db_id, txm_event_id=txm_event.db_id)
    elif txm_event.default_config_id is not None:
        return get_configuration_from_db_id(txm_event.default_config_id, txm_event_id=txm_event.db_id)
    else:
        return Configuration()


def get_config_id_for_configuration_or_save(configuration: Configuration,
                                            txm_event_id: int, user_id: int) -> int:
    maybe_config_id = find_config_id_for_configuration(configuration, txm_event_id)

    if maybe_config_id is not None:
        return maybe_config_id
    else:
        return save_configuration_to_db(configuration, txm_event_id, user_id)


def find_config_id_for_configuration(configuration: Configuration, txm_event_id: int) -> Optional[int]:
    logger.debug('Searching models for configuration')
    config_models = ConfigModel.query.filter(
        ConfigModel.txm_event_id == txm_event_id
    ).all()

    for config_model in config_models:
        config_from_model = configuration_from_config_model(config_model)
        if configuration == config_from_model:
            logger.debug(f'Found config for configuration with id {config_model.id}')
            return config_model.id

    logger.info(f'Configuration for event {txm_event_id} not found')
    return None
