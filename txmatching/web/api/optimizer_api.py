from flask_restx import Resource

from txmatching.auth.exceptions import InvalidOtpException, InvalidAuthCallException, \
    AuthenticationException
from txmatching.data_transfer_objects.optimizer.optimizer_in_swagger import \
    OptimizerReturnObjectJson, OptimizerRequestObjectJson
from txmatching.optimizer.optimizer_functions import export_return_data
from txmatching.optimizer.optimizer_request_object import OptimizerRequest
from txmatching.web.web_utils.namespaces import optimizer_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

OPTIMIZER_DESCRIPTION = "Endpoint that calculates matchings from compatibility graph and configuration"


# https://www.dropbox.com/home/KEP-SOFT_developers/optimizer_module?preview=Optimizer+Input+Schema+First+draft.docx&preview=Optimizer+Input+Schema+First+draft.docx
@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.request_body(OptimizerRequestObjectJson)
    @optimizer_api.response_ok(OptimizerReturnObjectJson, description=OPTIMIZER_DESCRIPTION)
    @optimizer_api.response_errors(exceptions=[KeyError,
                                               InvalidOtpException,
                                               AuthenticationException,
                                               InvalidAuthCallException])
    def post(self) -> str:
        optimizer_request_object = request_body(OptimizerRequest)

        # todo calculate cycles and chains

        # todo return files
        optimizer_return = export_return_data()
        return response_ok(optimizer_return)
