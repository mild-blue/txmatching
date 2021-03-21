from enum import Enum
from typing import TypeVar

from dacite import Config, Type, from_dict
from flask import jsonify, make_response, request

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
