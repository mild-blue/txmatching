import dataclasses
import logging
from datetime import datetime
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
                                                    PairingResultModel)
from txmatching.patients.patient import TxmEvent
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLACrossmatchLevel

logger = logging.getLogger(__name__)


def get_configuration_from_db_id(configuration_db_id: int) -> Configuration:
    config = ConfigModel.query.get(configuration_db_id)
    if config is None:
        raise AssertionError(f'Configuration not found for db id {configuration_db_id}')
    return configuration_from_dict(config.parameters)


def configuration_from_dict(config_model: Dict) -> Configuration:
    configuration = from_dict(data_class=Configuration,
                              data=config_model,
                              config=Config(cast=[Country, HLACrossmatchLevel]))
    return configuration


def get_latest_configuration_for_txm_event(txm_event: TxmEvent) -> Configuration:
    configuration_db_id = get_latest_configuration_db_id_for_txm_event(txm_event)
    if configuration_db_id is None:
        return Configuration()
    else:
        return get_configuration_from_db_id(configuration_db_id)


def save_configuration_to_db(configuration: Configuration, txm_event: TxmEvent, user_id: int) -> int:
    patients_hash = get_patients_persistent_hash(txm_event)
    config_model = _configuration_to_config_model(configuration, txm_event.db_id, patients_hash, user_id)

    db.session.add(config_model)
    db.session.commit()
    return config_model.id


def get_latest_configuration_db_id_for_txm_event(txm_event: TxmEvent) -> Optional[int]:
    patients_hash = get_patients_persistent_hash(txm_event)
    config = ConfigModel.query.filter(and_(
        ConfigModel.txm_event_id == txm_event.db_id,
        ConfigModel.patients_hash == patients_hash
    )).order_by(
        ConfigModel.updated_at.desc()
    ).first()
    if config:
        return config.id
    return None


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


def find_configuration_db_id_for_configuration(configuration: Configuration,
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
            logger.debug('Found config for configuration')
            return config_model.id

    logger.info(f'Configuration for event {txm_event.db_id} and patients hash {patients_hash} not found')
    return None


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


def config_set_updated(configuration_db_id: int):
    ConfigModel.query.filter(ConfigModel.id == configuration_db_id).update({'updated_at': datetime.now()})
    db.session.commit()
