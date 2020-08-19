from flask_restx import fields

from kidney_exchange.web.api.namespaces import matching_api

CONFIGURATION_MODEL = matching_api.model('Configuration', {
    "scorer_constructor_name": fields.String(required=False),
    "solver_constructor_name": fields.String(required=False),
    "enforce_compatible_blood_group": fields.Boolean(required=False),
    "minimum_total_score": fields.Float(required=False),
    "maximum_total_score": fields.Float(required=False),
    "require_new_donor_having_better_match_in_compatibility_index": fields.Boolean(required=False),
    "require_new_donor_having_better_match_in_compatibility_index_or_blood_group": fields.Boolean(required=False),
    "use_binary_scoring": fields.Boolean(required=False),
    "max_cycle_length": fields.Integer(required=False),
    "max_sequence_length": fields.Integer(required=False),
    "max_number_of_distinct_countries_in_round": fields.Integer(required=False),
    "required_patient_db_ids": fields.List(required=False, cls_or_instance=fields.Integer),
    "manual_donor_recipient_scores_dto": fields.String(required=False)
}
                                         )
