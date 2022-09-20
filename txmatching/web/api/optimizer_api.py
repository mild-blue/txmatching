from typing import Optional

from flask_restx import Resource

# todo require_valid_txm_event_id
from txmatching.auth.auth_check import (require_valid_config_id,
                                        require_valid_txm_event_id)
from txmatching.auth.exceptions import (AuthenticationException,
                                        InvalidAuthCallException,
                                        InvalidOtpException)
from txmatching.data_transfer_objects.configuration.configuration_swagger import \
    ConfigIdPathParamDefinition
from txmatching.data_transfer_objects.optimizer.optimizer_in_swagger import (
    OptimizerRequestObjectJson, OptimizerReturnObjectJson)
from txmatching.database.services.config_service import \
    get_configuration_parameters_from_db_id_or_default
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.optimizer.optimizer_functions import (
    export_return_data, get_compatibility_graph, get_optimizer_configuration,
    get_pairs_from_txm_event)
from txmatching.optimizer.optimizer_request_object import OptimizerRequest
from txmatching.web.web_utils.namespaces import optimizer_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

EXPORT_DESCRIPTION = 'Endpoint that exports data from TXM that can be input into optimization module'
OPTIMIZER_DESCRIPTION = 'Endpoint that calculates matchings from compatibility graph and configuration'


# https://www.dropbox.com/home/KEP-SOFT_developers/optimizer_module?preview=Optimizer+Input+Schema+First+draft.docx&preview=Optimizer+Input+Schema+First+draft.docx
@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.request_body(OptimizerRequestObjectJson)
    @optimizer_api.response_ok(OptimizerReturnObjectJson, description=OPTIMIZER_DESCRIPTION)
    @optimizer_api.response_errors(exceptions={KeyError,
                                               InvalidOtpException,
                                               AuthenticationException,
                                               InvalidAuthCallException})
    def post(self) -> str:
        optimizer_request_object = request_body(OptimizerRequest)

        # todo calculate cycles and chains

        # todo return files
        optimizer_return = export_return_data()
        return response_ok(optimizer_return)


@optimizer_api.route('/export/<txm_event_id>/<config_id>', methods=['GET'])
class Optimize(Resource):
    @optimizer_api.doc(
        params={
            'txm_event_id': {
                'description': 'Id of txm event chosen',
                'type': int,
                'in': 'path',
                'required': True
            },
            'config_id': ConfigIdPathParamDefinition
        }
    )
    @optimizer_api.response_ok(OptimizerRequestObjectJson, description=EXPORT_DESCRIPTION)
    @optimizer_api.response_ok(description=EXPORT_DESCRIPTION)
    @optimizer_api.response_errors(exceptions={KeyError,
                                               InvalidOtpException,
                                               AuthenticationException,
                                               InvalidAuthCallException})
    @optimizer_api.require_user_login()
    # @require_valid_txm_event_id()
    @require_valid_config_id()
    def get(self, txm_event_id: int, config_id: Optional[int]) -> str:
        txm_event = get_txm_event_complete(txm_event_id)
        txm_event_configuration_parameters = get_configuration_parameters_from_db_id_or_default(txm_event, config_id)

        # get pairs
        pairs = get_pairs_from_txm_event(txm_event.active_and_valid_donors_dict)

        # get compatibility graph
        compatibility_graph = get_compatibility_graph(txm_event.active_and_valid_donors_dict,
                                                      txm_event.active_and_valid_recipients_dict)

        # get configuration
        configuration = get_optimizer_configuration(txm_event_configuration_parameters)

        return response_ok(OptimizerRequest(
            compatibility_graph=compatibility_graph,
            pairs=pairs,
            configuration=configuration
        ))
