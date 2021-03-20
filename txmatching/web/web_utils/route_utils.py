from enum import Enum
from typing import TypeVar

from dacite import Config, Type, from_dict
from flask import jsonify, request

T = TypeVar('T')


def response_ok(data):
    return jsonify(data)


def request_body(data_class: Type[T]) -> T:
    return from_dict(
        data_class=data_class,
        data=request.json,
        config=Config(cast=[Enum])
    )
