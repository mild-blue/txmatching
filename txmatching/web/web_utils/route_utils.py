from enum import Enum
from typing import Optional, TypeVar

from dacite import Config, Type, from_dict
from flask import jsonify, make_response, request

from txmatching.auth.exceptions import InvalidArgumentException

# because this is not constant
# pylint: disable=invalid-name
T = TypeVar('T')


def response_ok(data, code=200):
    # TODO: marshall instead jsonify https://github.com/mild-blue/txmatching/issues/562
    return make_response(jsonify(data), code)


def request_body(data_class: Type[T]) -> T:
    return from_dict(
        data_class=data_class,
        data=request.json,
        config=Config(cast=[Enum])
    )


def request_arg_int(
        param: str,
        default: Optional[int] = None,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None
) -> int:
    """
    Get integer request parameter.
    """
    try:
        val = int(request.args.get(key=param, default=default))  # TODOO
        if (minimum is not None and val < minimum) or (maximum is not None and val > maximum):
            raise InvalidArgumentException(
                f'Query argument {param} must be in '
                f'range [{minimum}, {maximum}]. '
                f'Current value is {val}.'
            )
        return val
    except ValueError:
        if default is None:
            raise InvalidArgumentException(f'Query argument {param} must be set.')
        return default


def request_arg_bool(param: str, default: Optional[bool] = None) -> bool:
    """
    Get boolean request parameter.

    Example:
        True value:
        param=TrUe
        param=true
        param=1

        False value:
        param=FalSe
        param=false
        param=0

        Error:
        param=foo
        param=
    """
    try:
        val = str(request.args.get(key=param, default=default))
        if val.lower() in ['false', '0']:
            return False
        elif val.lower() in ['true', '1']:
            return True
        else:
            raise InvalidArgumentException(f'Query argument {param} has invalid value {val}. '
                                           f'Accepted values are: true, false, 1, 2.')
    except ValueError:
        if default is None:
            raise InvalidArgumentException(f'Query argument {param} must be set.')
        return default


def request_arg_flag(param: str) -> bool:
    """
    Returns whether the request parameter is set.

    :param param: Parameter name
    :return: True if parameter is provided, False if not provided
    """
    return param in request.args
