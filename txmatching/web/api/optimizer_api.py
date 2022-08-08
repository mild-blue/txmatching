import logging

from flask_restx import Resource
from flask import request, Response
from typing import List
from werkzeug.datastructures import FileStorage

from txmatching.optimizer.optimizer_functions import export_return_data, parse_csv_to_comp_info, parse_csv_to_pairs, \
    parse_json_to_config
from txmatching.web.web_utils.namespaces import optimizer_api

logger = logging.getLogger(__name__)

FILES = {'configuration': 'json', 'pairs': 'csv', 'compatibility_graph': 'csv'}

# todo swagger ignores my formatting tabs
OPTIMIZER_DESCRIPTION = '''
Endpoint that accepts 3 input files: 
1. pairs (csv) in format:
original_donor_index, original_recipient_index
2,1
3,1

2. compatibility_graph (csv) in format:
donor_index, recipient_index, hla_compatibility_score, donor_age_difference...
1,2,17,1
2,2,18,1
1,3,8,5
1,4,19,10

3. configuration (json) in format:
{
    limitations: {
        max_cycle_length: 3
        max_chain_length: 3
        custom_algorithm_settings: {
            max_number_of_iterations: 200
        }
    },
    scoring: {
        [
            [{transplant_count, 1}],
            [{hla_compatibility_score: 3}, {number of donor_age_difference: 20}],
            [{max_num_effective_two_cycles: 1}]
        ]
    }
}

Computes cycles and chains.

Outputs two files:

1. selected_cycles.csv with columns:
donor_id, recipient_id, cycle_or_chain_id, index_in_cycle, weighted_score

2. matching_stats.csv with columns:
level_of_optimization, prio_highly_sensitized_recipients, max_num_of_transplants, number_of_patients
'''


def check_extensions(files: List[FileStorage]):
    for file in files:
        name = file.name
        extension = file.filename.rsplit('.', 1)[1].lower()
        if not '.' in file.filename or FILES[name] != extension:
            raise ValueError(f'File \'{name}\' not in correct format.')


@optimizer_api.route('', methods=['POST'])
class Optimize(Resource):
    @optimizer_api.response_ok(description=OPTIMIZER_DESCRIPTION)
    @optimizer_api.response_errors()
    def post(self) -> Response:
        for file in FILES:
            if file not in request.files:
                raise ValueError(f'Missing file \'{file}\'.')

        comp_graph_f = request.files['compatibility_graph']
        config_f = request.files['configuration']
        pairs_f = request.files['pairs']

        check_extensions([comp_graph_f, config_f, pairs_f])

        # parse to objects and validate
        comp_info_prep = parse_csv_to_comp_info(comp_graph_f)
        comp_info = parse_csv_to_pairs(pairs_f, comp_info_prep)
        config = parse_json_to_config(config_f)

        # todo calculate cycles and chains

        # todo return files
        response = export_return_data()
        return response
