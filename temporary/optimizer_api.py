from flask import jsonify, make_response, Response, request
from flask_restx import Resource

import json
import os

from namespace import Namespace
from optimiser import input_path, main, output_path
# TODO: use swagger to describe the API structure and generate the documentation
from optimizer_in_swagger import OptimizerReturnObjectJson, OptimizerRequestObjectJson

OPTIMIZER_DESCRIPTION = "Endpoint that calculates matchings from compatibility graph and configuration"
INPUT_PATH = input_path
OUTPUT_PATH = output_path
OPTIMIZER_NAMESPACE = 'optimizer'
optimizer_api = Namespace(OPTIMIZER_NAMESPACE)


# https://www.dropbox.com/home/KEP-SOFT_developers/optimizer_module?preview=Optimizer+Input+Schema+First+draft.docx&preview=Optimizer+Input+Schema+First+draft.docx
@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.request_body(OptimizerRequestObjectJson)
    @optimizer_api.response_ok(OptimizerReturnObjectJson, description=OPTIMIZER_DESCRIPTION)
    def post(self) -> Response:
        optimizer_request_object = request.json

        with open(INPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(optimizer_request_object, f, ensure_ascii=False, indent=4)

        main(INPUT_PATH, OUTPUT_PATH)

        output_file = open(OUTPUT_PATH)
        optimizer_return = json.load(output_file)

        os.remove(INPUT_PATH)
        os.remove(OUTPUT_PATH)

        return make_response(jsonify(optimizer_return))
