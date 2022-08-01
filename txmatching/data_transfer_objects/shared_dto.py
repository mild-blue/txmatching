from dataclasses import dataclass
from txmatching.database.services.txm_event_service import does_txm_event_exist
from txmatching.configuration.configuration import does_configuration_exist

@dataclass
class SuccessDTOOut:
    success: bool

# pylint:enable=invalid-name
@dataclass
class IdentifierDTOIn:
    # pylint:disable=invalid-name
    id: int
    # pylint:enable=invalid-name

    def __post_init__(self): # to do: check whether the identifier exists (and check all other id fields)
        does_configuration_exist(self.id)


# def does_configuration_exist(configuration_id):
#     return ConfigModel.query.filter_by(id=configuration_id).first() is not None