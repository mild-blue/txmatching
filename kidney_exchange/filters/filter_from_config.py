from kidney_exchange.config.configuration import Configuration
from kidney_exchange.filters.filter_base import FilterBase
from kidney_exchange.filters.filter_default import FilterDefault
from kidney_exchange.utils.construct_configurable_object import construct_configurable_object

_supported_filters = [FilterDefault]


def filter_from_config(config: Configuration) -> FilterBase:
    # TODO add filter to config when we have more of them
    return construct_configurable_object("FilterDefault", _supported_filters, config)
