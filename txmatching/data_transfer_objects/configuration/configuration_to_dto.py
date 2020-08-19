import dataclasses
from typing import Tuple, Union

from txmatching.config.configuration import (MAN_DON_REC_SCORES,
                                                  Configuration,
                                                  DonorRecipientScore)
from txmatching.data_transfer_objects.configuration.configuration_dto import ConfigurationDTO, \
    MAN_DON_REC_SCORES_DTO
from txmatching.database.services.patient_service import \
    db_id_to_medical_id


def _score_to_dto(score: Union[float, str]) -> float:
    if isinstance(score, (float, int)):
        return score
    else:
        return -1


def _donor_recipient_score_to_dto(self: DonorRecipientScore) -> Tuple[str, str, float]:
    return (
        db_id_to_medical_id(self.donor_id),
        db_id_to_medical_id(self.recipient_id),
        _score_to_dto(self.score)
    )


def configuration_to_dto(configuration: Configuration) -> ConfigurationDTO:
    configuration_dto = dataclasses.asdict(configuration)
    configuration_dto[MAN_DON_REC_SCORES_DTO] = [
        _donor_recipient_score_to_dto(don_rec_score) for don_rec_score in
        configuration.manual_donor_recipient_scores]
    del configuration_dto[MAN_DON_REC_SCORES]

    return ConfigurationDTO(**configuration_dto)
