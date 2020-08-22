from txmatching.config.configuration import Configuration
from txmatching.filters.filter_base import FilterBase
from txmatching.filters.filter_default import FilterDefault
from txmatching.utils.construct_configurable_object import construct_configurable_object

_supported_filters = [FilterDefault]


def filter_from_config(config: Configuration) -> FilterBase:
    # TODO handle filter properly: do all the stuff of filter already in solver and scorer https://trello.com/c/Cn2HCKLX
    return construct_configurable_object("FilterDefault", _supported_filters, config)
