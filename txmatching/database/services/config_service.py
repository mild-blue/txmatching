import dataclasses
import logging
from typing import Dict, Optional

from dacite import Config, from_dict
from sqlalchemy import and_

from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.data_transfer_objects.matchings.pairing_result import \
    DatabasePairingResult
from txmatching.database.db import db
from txmatching.database.services.patient_service import \
    get_patients_persistent_hash
from txmatching.database.sql_alchemy_schema import (ConfigModel,
                                                    PairingResultModel,
                                                    TxmEventModel)
from txmatching.patients.patient import TxmEvent
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLACrossmatchLevel

logger = logging.getLogger(__name__)


def configuration_from_dict(config_model: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_model,
                              config=Config(cast=[Country, HLACrossmatchLevel]))
    return configuration


def save_configuration_to_db(configuration: Configuration, txm_event: TxmEvent, user_id: int) -> int:
    patients_hash = get_patients_persistent_hash(txm_event)
    config_model = _configuration_to_config_model(configuration, txm_event.db_id, patients_hash, user_id)

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
        patients_hash: int,
        user_id: int
) -> ConfigModel:
    return ConfigModel(
        parameters=dataclasses.asdict(configuration),
        txm_event_id=txm_event_db_id,
        patients_hash=patients_hash,
        created_by=user_id
    )


def _get_configuration_from_db_id(configuration_db_id: int, txm_event_id: int) -> Configuration:
    config = ConfigModel.query.get(configuration_db_id)
    if config is None:
        # As txm_event.default_config_id column is integer and not linked to config.id
        # (see comment in sql_alchemy_schema), it can happen that default_config_id is set while corresponding config
        # is deleted. Such problem happens in TestSwaggerEndpoint. For this reason, we handle it by returning default
        # configuration instance.
        logger.error(f'Configuration not found for db id {configuration_db_id}. Returning default configuration.')
        return Configuration()
    if txm_event_id != config.txm_event_id:
        logger.error(f'Configuration with db id {configuration_db_id} does '
                     f'not belong to txm event {txm_event_id}. Returning default configuration')
        return Configuration()

    return configuration_from_dict(config.parameters)


def get_configuration_from_db_id_or_default(txm_event: TxmEvent, configuration_db_id: Optional[int]) -> Configuration:
    """
    Return configuration and does not check patient hash.
    - if specified, return configuration by configuration_db_id
    - otherwise, if specified, return default configuration of txm event
    - otherwise, return default Configuration() object
    """
    if configuration_db_id is not None:
        return _get_configuration_from_db_id(configuration_db_id, txm_event_id=txm_event.db_id)
    elif txm_event.default_config_id is not None:
        return _get_configuration_from_db_id(txm_event.default_config_id, txm_event_id=txm_event.db_id)
    else:
        return Configuration()


def find_config_db_id_for_configuration_and_data(configuration: Configuration,
                                                 txm_event: TxmEvent) -> Optional[int]:
    logger.debug('Searching models for configuration')
    patients_hash = get_patients_persistent_hash(txm_event)
    config_models = ConfigModel.query.filter(and_(
        ConfigModel.txm_event_id == txm_event.db_id,
        ConfigModel.patients_hash == patients_hash
    )).all()

    for config_model in config_models:
        config_from_model = configuration_from_dict(config_model.parameters)
        if configuration.comparable(config_from_model):
            logger.debug(f'Found config for configuration with id {config_model.id}')

            return config_model.id

    logger.info(f'Configuration for event {txm_event.db_id} and patients hash {patients_hash} not found')
    return None


def update_max_matchings_to_show_to_viewer(configuration_id: int, configuration: Configuration):
    config_model = ConfigModel.query.get(configuration_id)
    config_model.parameters['max_matchings_to_show_to_viewer'] = configuration.max_matchings_to_show_to_viewer
    ConfigModel.query.filter(ConfigModel.id == config_model.id).update(
        {'parameters': config_model.parameters}
    )
    db.session.commit()


def get_pairing_result_for_configuration_db_id(configuration_db_id: int) -> DatabasePairingResult:
    pairing_result_model = (
        PairingResultModel
            .query.filter(PairingResultModel.config_id == configuration_db_id)
            .first()
    )
    if pairing_result_model is None:
        raise AssertionError(f'Pairing result for given configuration db id {configuration_db_id} '
                             f'does not exist. But this should always be true for all configs.')
    matchings = from_dict(data_class=MatchingsModel,
                          data=pairing_result_model.calculated_matchings)
    score_matrix = pairing_result_model.score_matrix['score_matrix_dto']
    return DatabasePairingResult(score_matrix=score_matrix, matchings=matchings)
