from flask_restx import fields

from txmatching.utils.enums import HLA_GROUPS_GENE, MatchTypes, HLAGroups
from txmatching.web.api.namespaces import matching_api

EXAMPLE_DETAILED_SCORE = {
    HLAGroups.A.name: {
        "donor_matches": {
            "A23": MatchTypes.BROAD.name,
            "A1": MatchTypes.SPLIT.name
        },
        "recipient_matches": {
            "A9": MatchTypes.BROAD.name,
            "A1": MatchTypes.SPLIT.name
        },
        "group_compatibility_index": 2.0
    },
    HLAGroups.B.name: {
        "donor_matches": {},
        "recipient_matches": {},
        "group_compatibility_index": 0.0
    },
    HLAGroups.DRB1.name: {
        "donor_matches": {},
        "recipient_matches": {},
        "group_compatibility_index": 0.0
    }
}

TransplantJson = matching_api.model('Transplant', {
    'score': fields.Float(required=True),
    'compatible_blood': fields.Boolean(required=True),
    'donor': fields.String(required=True),
    'recipient': fields.String(required=True),
    'detailed_compatibility_index': fields.Raw(
        required=True,
        description=f"Contains details for compatibility index for each HLA Group compatibility"
                    f" index is calculated for. Current groups are:"
                    f"{[group.name for group in HLA_GROUPS_GENE]}. The fields provided are:"
                    f"donor_matches, recipient_matches, group_compatibility_index"
                    f"where donor_matches and recipient_matches are dicts of hla codes that"
                    f"are the same for give transplant and that should be colored."
                    f"The dict values are then type of match. Which is of the following types:"
                    f"{[match_type.name for match_type in MatchTypes]}",
        example=EXAMPLE_DETAILED_SCORE),
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
