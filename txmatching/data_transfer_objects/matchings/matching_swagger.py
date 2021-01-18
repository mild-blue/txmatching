from flask_restx import fields

from txmatching.data_transfer_objects.hla.hla_swagger import (HLAAntibody,
                                                              HLAType)
from txmatching.utils.enums import (HLA_GROUPS_NAMES_WITH_OTHER,
                                    AntibodyMatchTypes, HLAGroup, MatchTypes)
from txmatching.web.api.namespaces import matching_api

EXAMPLE_DETAILED_SCORE = [
    {'hla_group': HLAGroup.A.name,
     'donor_matches': [
         {'hla_code': {'code': 'A23', 'raw_code': 'A23'},
          'match_type': MatchTypes.BROAD.name},
         {'hla_code': {'code': 'A1', 'raw_code': 'A1'},
          'match_type': MatchTypes.SPLIT.name}
     ],
     'recipient_matches': [
         {'hla_code': {'code': 'A9', 'raw_code': 'A9'},
          'match_type': MatchTypes.BROAD.name},
         {'hla_code': {'code': 'A1', 'raw_code': 'A1'},
          'match_type': MatchTypes.SPLIT.name}
     ],
     'antibody_matches': [
         {'hla_code': 'A9',
          'match_type': AntibodyMatchTypes.NONE.name},
         {'hla_code': 'A1',
          'match_type': AntibodyMatchTypes.MATCH.name}
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
     },
    {'hla_group': HLAGroup.Other.name,
     'donor_matches': [],
     'recipient_matches': [],
     'antibody_matches': [],
     'group_compatibility_index': 0.0
     }
]

DESCRIPTION_DETAILED_SCORE = """Contains details for compatibility index for each HLA Group compatibility
index is calculated for."""

AntigenMatchJson = matching_api.model('AntigenMatch', {
    'hla_code': fields.Nested(required=True, model=HLAType),
    'match_type': fields.String(required=True, enum=[match_type.name for match_type in MatchTypes])
})

AntibodyMatchJson = matching_api.model('AntibodyMatch', {
    'hla_code': fields.Nested(required=True, model=HLAAntibody),
    'match_type': fields.String(required=True, enum=[match_type.name for match_type in AntibodyMatchTypes])
})

DetailedScoreForGroupJson = matching_api.model('DetailedScoreForGroup', {
    'hla_group': fields.String(required=True, enum=[group.name for group in HLA_GROUPS_NAMES_WITH_OTHER]),
    'donor_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntigenMatchJson)),
    'recipient_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntigenMatchJson)),
    'group_compatibility_index': fields.Float(required=True, example=2.0),
    'antibody_matches': fields.List(required=True, cls_or_instance=fields.Nested(AntibodyMatchJson))
})

TransplantJson = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True),
    # Unfortunately is raw as we want to have the model general it is not clear how many different hla_groups will
    # we have and I do not know better way how to have here a dict with unspecified keys.
    'detailed_score_per_group': fields.List(
        required=True,
        description=DESCRIPTION_DETAILED_SCORE,
        example=EXAMPLE_DETAILED_SCORE,
        cls_or_instance=fields.Nested(DetailedScoreForGroupJson))
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
