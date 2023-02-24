from flask_restx import fields

from txmatching.data_transfer_objects.hla.hla_swagger import (HLAAntibody,
                                                              HLAType)
from txmatching.utils.enums import (HLA_GROUPS,
                                    AntibodyMatchTypes, HLAAntibodyType, HLAGroup, MatchType)
from txmatching.web.web_utils.namespaces import matching_api

_CODE_A1 = {'high_res': None, 'split': None, 'broad': 'A1'}
_CODE_A23 = {'high_res': None, 'split': None, 'broad': 'A23'}
_CODE_A9 = {'high_res': None, 'split': None, 'broad': 'A9'}

EXAMPLE_DETAILED_SCORE = [
    {'hla_group': HLAGroup.A.name,
     'donor_matches': [
         {'hla_type': {'code': _CODE_A23, 'raw_code': 'A23'},
          'match_type': MatchType.BROAD.name},
         {'hla_type': {'code': _CODE_A1, 'raw_code': 'A1'},
          'match_type': MatchType.SPLIT.name}
     ],
     'recipient_matches': [
         {'hla_type': {'code': _CODE_A9, 'raw_code': 'A9'},
          'match_type': MatchType.BROAD.name},
         {'hla_type': {'code': _CODE_A1, 'raw_code': 'A1'},
          'match_type': MatchType.SPLIT.name}
     ],
     'antibody_matches': [
         {'hla_antibody': {'raw_code': 'A9', 'mfi': 0, 'cutoff': 0, 'code': _CODE_A9, 'type': HLAAntibodyType.NORMAL.name},
          'match_type': AntibodyMatchTypes.NONE.name},
         {'hla_antibody': {'raw_code': 'A1', 'mfi': 0, 'cutoff': 0, 'code': _CODE_A1, 'type': HLAAntibodyType.NORMAL.name},
          'match_type': AntibodyMatchTypes.BROAD.name}
     ],
     'group_compatibility_index': 2.0
     },
    {'hla_group': HLAGroup.B.name,
     'donor_matches': [],
     'recipient_matches': [],
     'antibody_matches': [],
     'group_compatibility_index': 0.0
     },
    {'hla_group': HLAGroup.DRB1.name,
     'donor_matches': [],
     'recipient_matches': [],
     'antibody_matches': [],
     'group_compatibility_index': 0.0
     }
]

DESCRIPTION_DETAILED_SCORE = """Contains details for compatibility index for each HLA Group compatibility
index is calculated for."""

AntigenMatchJson = matching_api.model('AntigenMatch', {
    'hla_type': fields.Nested(required=True, model=HLAType),
    'match_type': fields.String(required=True, enum=[match_type.name for match_type in MatchType])
})

AntibodyMatchJson = matching_api.model('AntibodyMatch', {
    'hla_antibody': fields.Nested(required=True, model=HLAAntibody),
    'match_type': fields.String(required=True, enum=[match_type.name for match_type in AntibodyMatchTypes])
})

DetailedScoreForGroupJson = matching_api.model('DetailedScoreForGroup', {
    'hla_group': fields.String(required=True, enum=[group.name for group in HLA_GROUPS]),
    'donor_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntigenMatchJson)),
    'recipient_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntigenMatchJson)),
    'group_compatibility_index': fields.Float(required=True, example=2.0),
    'antibody_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntibodyMatchJson))
})

TransplantParsingIssueMessagesJson = matching_api.model('AllTransplantMessages', {
    'infos': fields.List(fields.String),
    'warnings': fields.List(fields.String),
    'errors': fields.List(fields.String)
})

TransplantWarningsJson = matching_api.model('TransplantWarning', {
    'message_global': fields.String(),
    'all_messages': fields.Nested(TransplantParsingIssueMessagesJson)
})

TransplantJson = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'max_score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True),
    # Unfortunately is raw as we want to have the model general it is not clear how many different hla_groups will
    # we have and I do not know better way how to have here a dict with unspecified keys.
    'detailed_score_per_group': fields.List(
        required=True,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroupJson)),
    'transplant_messages': fields.Nested(TransplantWarningsJson)
})

CountryInRoundJson = matching_api.model('Country', {
    'country_code': fields.String(required=True),
    'donor_count': fields.Integer(required=True),
    'recipient_count': fields.Integer(required=True)
})

RoundJson = matching_api.model('Round', {
    'transplants': fields.List(cls_or_instance=fields.Nested(TransplantJson))
})

MatchingJson = matching_api.model('Matching', {
    'score': fields.Float(required=True),
    'rounds': fields.List(required=True, cls_or_instance=fields.Nested(RoundJson)),
    'countries': fields.List(required=True, cls_or_instance=fields.Nested(CountryInRoundJson)),
    'order_id': fields.Integer(required=True),
    'count_of_transplants': fields.Integer(required=True)
})

CalculatedMatchingsJson = matching_api.model('CalculatedMatchings', {
    'calculated_matchings': fields.List(required=True, cls_or_instance=fields.Nested(MatchingJson)),
    'number_of_possible_transplants': fields.Integer(required=False),
    'number_of_possible_recipients': fields.Integer(required=False),
    'config_id': fields.Integer(required=True)
})

RecipientDonorCompatibilityDetailsJson = matching_api.model('RecipientDonorCompatibilityDetails', {
    'recipient_db_id': fields.Integer(required=True, description='Database id of the recipient', example=1),
    'donor_db_id': fields.Integer(required=True, description='Database id of the donor', example=1),
    'score': fields.Float(required=True, description='Compatibility score if donor and recipient'),
    'max_score': fields.Float(required=True, description='Maximum transplant score'),
    'compatible_blood': fields.Boolean(
        required=True,
        description='Indicator whether donor and recipient have compatible blood groups'
    ),
    'detailed_score': fields.List(
        required=True,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroupJson)
    ),
})
