from flask_restx import fields

from txmatching.utils.country import Country
from txmatching.web.api.namespaces import matching_api

MANUAL_DONOR_RECIPIENT_SCORE_JSON = matching_api.model("Manual Recipient Donor Score", {
    "donor_db_id": fields.Integer(required=True),
    "recipient_db_id": fields.Integer(required=True),
    "score": fields.Float(required=True)
})

FORBIDDEN_COUNTRY_COMBINATION = matching_api.model("Forbidden Country Combination", {
    "donor_country": fields.String(required=True, enum=[country.name for country in Country]),
    "recipient_country": fields.String(required=True, enum=[country.name for country in Country]),
})

CONFIGURATION_JSON = matching_api.model(
    'Configuration',
    {
        "scorer_constructor_name": fields.String(required=False),
        "solver_constructor_name": fields.String(required=False),
        "enforce_compatible_blood_group": fields.Boolean(required=False),
        "minimum_total_score": fields.Float(required=False),
        "maximum_total_score": fields.Float(required=False),
        "require_new_donor_having_better_match_in_compatibility_index": fields.Boolean(required=False),
        "require_new_donor_having_better_match_in_compatibility_index_or_blood_group": fields.Boolean(required=False),
        "blood_group_compatibility_bonus": fields.Float(required=False),
        "use_binary_scoring": fields.Boolean(required=False),
        "max_cycle_length": fields.Integer(required=False),
        "max_sequence_length": fields.Integer(required=False),
        "max_number_of_distinct_countries_in_round": fields.Integer(required=False),
        "required_patient_db_ids": fields.List(required=False, cls_or_instance=fields.Integer),
        "allow_low_high_res_incompatible": fields.Boolean(required=False),
        "manual_donor_recipient_scores": fields.List(required=False, cls_or_instance=fields.Nested(
            MANUAL_DONOR_RECIPIENT_SCORE_JSON)),
        "forbidden_country_combinations": fields.List(required=False, cls_or_instance=fields.Nested(
            FORBIDDEN_COUNTRY_COMBINATION)),
        "max_matchings_to_show_to_viewer": fields.Integer(required=False)
    }
)
