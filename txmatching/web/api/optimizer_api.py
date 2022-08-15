from flask_restx import Resource

from txmatching.data_transfer_objects.optimizer.optimizer_in_swagger import \
    OptimizerReturnObjectJson, OptimizerRequestObjectJson
from txmatching.optimizer.optimizer_functions import export_return_data
from txmatching.optimizer.optimizer_request_object import OptimizerRequest
from txmatching.web.web_utils.namespaces import optimizer_api
from txmatching.web.web_utils.route_utils import request_body, response_ok

# todo swagger ignores my formatting tabs
# todo toto asi netreba a staci dat do swaggeru examples
OPTIMIZER_DESCRIPTION = '''
Endpoint that accepts 1 input json body: 
{
   "compatibility_graph":[
      {
         "donor_index":1,
         "recipient_index":2,
         "hla_compatibility_score":17,
         "donor_age_difference":1
      },
      {
         "donor_index":5,
         "recipient_index":7,
         "hla_compatibility_score":1,
         "donor_age_difference":4
      }
   ],
   "pairs":[
      {
         "donor_index":4,
         "recipient_index":2
      },
      {
         "donor_index":2
      }
   ],
   "configuration":{
      "limitations":{
         "max_cycle_length":3,
         "max_chain_length":3,
         "custom_algorithm_settings":{
            "max_number_of_iterations":200
         }
      },
      "scoring":[
         [
            {
               "transplant_count":1
            }
         ],
         [
            {
               "hla_compatibility_score":3
            },
            {
               "donor_age_difference":20
            }
         ],
         [
            {
               "num_effective_two_cycles":1
            }
         ]
      ]
   }
}
'''


@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.request_body(OptimizerRequestObjectJson)
    @optimizer_api.response_ok(OptimizerReturnObjectJson, description=OPTIMIZER_DESCRIPTION)
    @optimizer_api.response_errors()
    def post(self) -> str:
        optimizer_request_object = request_body(OptimizerRequest)
        print(optimizer_request_object)
        # todo calculate cycles and chains

        # todo return files
        return response_ok(export_return_data())
