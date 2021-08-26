from typing import Callable, List

from txmatching.configuration.config_parameters import ConfigParameters


def construct_configurable_object(object_name: str, supported_objects: List[Callable],
                                  config_parameters: ConfigParameters):
    constructor_dict = {supported_object.__name__: supported_object for supported_object in supported_objects}
    constructor = constructor_dict.get(object_name)
    if constructor is None:
        raise NotImplementedError(f'{object_name} not supported yet')
    return constructor.from_config(config_parameters)
