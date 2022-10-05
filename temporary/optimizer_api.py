from enum import Enum
from flask import jsonify, make_response, Response, request
from flask_restx import Resource

import json
import os

from dacite import Config, Type, from_dict
from namespace import Namespace
from optimiser import input_path, main, output_path
# TODO: use swagger to describe the API structure and generate the documentation
from optimizer_in_swagger import OptimizerReturnObjectJson, OptimizerRequestObjectJson
from optimizer_request_object import OptimizerRequest
from optimizer_return_object import OptimizerReturn
from typing import TypeVar

OPTIMIZER_DESCRIPTION = "Endpoint that calculates matchings from compatibility graph and configuration"
INPUT_PATH = input_path
OUTPUT_PATH = output_path
OPTIMIZER_NAMESPACE = 'optimizer'
optimizer_api = Namespace(OPTIMIZER_NAMESPACE)
T = TypeVar('T')

def _convert_json_to_dataclass(data_class: Type[T], json_file) -> T:
    return from_dict(
        data_class=data_class,
        data=json_file,
        config=Config(cast=[Enum])
    )

# https://www.dropbox.com/home/KEP-SOFT_developers/optimizer_module?preview=Optimizer+Input+Schema+First+draft.docx&preview=Optimizer+Input+Schema+First+draft.docx
@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.request_body(OptimizerRequestObjectJson)
    @optimizer_api.response_ok(OptimizerReturnObjectJson, description=OPTIMIZER_DESCRIPTION)
    def post(self) -> Response:
        optimizer_request = request.json

        with open(INPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(optimizer_request, f, ensure_ascii=False, indent=4)

        main(INPUT_PATH, OUTPUT_PATH)

        output_file = open(OUTPUT_PATH)
        optimizer_return = json.load(output_file)

        os.remove(INPUT_PATH)
        os.remove(OUTPUT_PATH)

        # check whether the input is in correct format
        _convert_json_to_dataclass(OptimizerRequest, optimizer_request)
        # check whether the output is un correct format
        _convert_json_to_dataclass(OptimizerReturn, optimizer_return)

        return make_response(jsonify(optimizer_return))
