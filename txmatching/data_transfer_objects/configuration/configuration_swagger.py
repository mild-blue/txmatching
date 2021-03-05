from flask_restx import fields

from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.enums_swagger import CountryCodeJson
from txmatching.solvers.solver_from_config import SUPPORTED_SOLVERS
from txmatching.web.api.namespaces import matching_api

ManualDonorRecipientScoreJson = matching_api.model('ManualRecipientDonorScore', {
    'donor_db_id': fields.Integer(required=True, example=2),
    'recipient_db_id': fields.Integer(required=True, example=3),
    'score': fields.Float(required=True, example=2.0)
})

ForbiddenCountryCombination = matching_api.model('ForbiddenCountryCombination', {
    'donor_country': fields.Nested(CountryCodeJson, required=True),
    'recipient_country': fields.Nested(CountryCodeJson, required=True),
})
_default_configuration = Configuration()
ConfigurationJson = matching_api.model(
    'Configuration',
    {
        'scorer_constructor_name': fields.String(required=True,
                                                 example=_default_configuration.scorer_constructor_name),
        'solver_constructor_name': fields.String(required=True,
                                                 example=_default_configuration.solver_constructor_name,
                                                 enum=[solver.__name__ for solver in SUPPORTED_SOLVERS]),
        'require_compatible_blood_group': fields.Boolean(required=True,
                                                         example=_default_configuration.require_compatible_blood_group),
        'minimum_total_score': fields.Float(required=True, example=_default_configuration.minimum_total_score),
        'maximum_total_score': fields.Float(required=True, example=_default_configuration.maximum_total_score),
        'require_better_match_in_compatibility_index': fields.Boolean(
            required=True,
            example=_default_configuration.require_better_match_in_compatibility_index
        ),
        'require_better_match_in_compatibility_index_or_blood_group': fields.Boolean(
            required=True,
            example=_default_configuration.require_better_match_in_compatibility_index_or_blood_group
        ),
        'blood_group_compatibility_bonus': fields.Float(
            required=True,
            example=_default_configuration.blood_group_compatibility_bonus
        ),
        'use_binary_scoring': fields.Boolean(required=True, example=_default_configuration.use_binary_scoring),
        'max_cycle_length': fields.Integer(required=True, example=_default_configuration.max_cycle_length),
        'max_sequence_length': fields.Integer(required=True, example=_default_configuration.max_sequence_length),
        'max_number_of_distinct_countries_in_round': fields.Integer(
            required=True,
            example=_default_configuration.max_number_of_distinct_countries_in_round
        ),
        'required_patient_db_ids': fields.List(required=True, cls_or_instance=fields.Integer,
                                               example=_default_configuration.required_patient_db_ids),
        'use_high_res_resolution': fields.Boolean(required=True,
                                                  example=_default_configuration.use_high_res_resolution),
        'forbidden_country_combinations': fields.List(required=True, cls_or_instance=fields.Nested(
            ForbiddenCountryCombination)),
        'manual_donor_recipient_scores': fields.List(required=True, cls_or_instance=fields.Nested(
            ManualDonorRecipientScoreJson)),
        'max_matchings_to_show_to_viewer': fields.Integer(
            required=True,
            example=_default_configuration.max_matchings_to_show_to_viewer
        ),
        'max_number_of_matchings': fields.Integer(
            required=True,
            example=_default_configuration.max_number_of_matchings
        ),
        'max_matchings_in_all_solutions_solver': fields.Integer(
            required=True,
            example=_default_configuration.max_matchings_in_all_solutions_solver
        ),
        'max_cycles_in_all_solutions_solver': fields.Integer(
            required=True,
            example=_default_configuration.max_cycles_in_all_solutions_solver
        ),
        'max_matchings_in_ilp_solver': fields.Integer(
            required=True,
            example=_default_configuration.max_matchings_in_ilp_solver
        )
    }
)
