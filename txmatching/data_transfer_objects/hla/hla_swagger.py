from flask_restx import fields

from txmatching.data_transfer_objects.enums_swagger import HLAAntibodyTypeJson
from txmatching.utils.enums import HLA_GROUPS, HLAGroup, HLAAntibodyType
from txmatching.web.web_utils.namespaces import patient_api

HLA_TYPES_PER_GROUPS_EXAMPLE = [
    {'hla_group': HLAGroup.A.name,
     'hla_types': [{'code': {'high_res': None, 'split': None, 'broad': 'A1'},
                    'raw_code': 'A1'}]},
    {'hla_group': HLAGroup.B.name,
     'hla_types': [{'code': {'high_res': None, 'split': None, 'broad': 'B38'},
                    'raw_code': 'B38'}]},
    {'hla_group': HLAGroup.DRB1.name,
     'hla_types': [{'code': {'high_res': None, 'split': None, 'broad': 'DR7'},
                    'raw_code': 'DR7'}]},
    {'hla_group': HLAGroup.CW.name,
     'hla_types': [{'code': {'high_res': None, 'split': None, 'broad': 'CW4'},
                    'raw_code': 'CW4'}]}
]
HLA_ANTIBODIES_PER_GROUPS_EXAMPLE = [
    {'hla_group': HLAGroup.A.name,
     'hla_antibody_list': [{
         'code': {'high_res': None, 'split': None, 'broad': 'A1'},
         'raw_code': 'A1', 'mfi': 0, 'cutoff': 0, 'type': HLAAntibodyType.NORMAL.name
     }]},
    {'hla_group': HLAGroup.B.name,
     'hla_antibody_list': [{
         'code': {'high_res': None, 'split': None, 'broad': 'B38'},
         'raw_code': 'B38', 'mfi': 10, 'cutoff': 0, 'type': HLAAntibodyType.NORMAL.name
     }]},
    {'hla_group': HLAGroup.DRB1.name,
     'hla_antibody_list': [{
         'code': {'high_res': None, 'split': None, 'broad': 'DR7'},
         'raw_code': 'DR7', 'mfi': 0, 'cutoff': 300, 'type': HLAAntibodyType.NORMAL.name
     }]},
    {'hla_group': HLAGroup.CW.name,
     'hla_antibody_list': [{
         'code': {'high_res': None, 'split': None, 'broad': 'CW4'},
         'raw_code': 'CW4', 'mfi': 500, 'cutoff': 500, 'type': HLAAntibodyType.NORMAL.name
     }]}
]
EXAMPLE_HLA_TYPING = {'hla_types_list': [{'raw_code': 'A*01:02'},
                                         {'raw_code': 'B7'},
                                         {'raw_code': 'DR11'}]}

HLACode = patient_api.model('HlaCode', {
    'high_res': fields.String(required=False),
    'split': fields.String(required=False),
    'broad': fields.String(required=True),
    'group': fields.String(required=False, enum=[group.name for group in HLA_GROUPS]),
})

HLAType = patient_api.model('HlaType', {
    'code': fields.Nested(HLACode, required=True),
    'raw_code': fields.String(required=True),
})

HLATypeRaw = patient_api.model('HlaTypeRaw', {
    'raw_code': fields.String(required=True, example='A32', description='Antigen raw code'),
})

HlaPerGroup = patient_api.model('HlaCodesInGroups', {
    'hla_group': fields.String(required=True, enum=[group.name for group in HLA_GROUPS]),
    'hla_types': fields.List(required=True, cls_or_instance=fields.Nested(HLAType))
})

HLATyping = patient_api.model('HlaTyping', {
    'hla_types_raw_list': fields.List(required=True, cls_or_instance=fields.Nested(HLATypeRaw)),
    'hla_per_groups': fields.List(required=True,
                                  description='hla types split to hla groups',
                                  example=HLA_TYPES_PER_GROUPS_EXAMPLE,
                                  cls_or_instance=fields.Nested(HlaPerGroup)),
})

HLAAntibody = patient_api.model('HlaAntibody', {
    'raw_code': fields.String(required=True),
    'second_raw_code': fields.String(required=False),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.Integer(required=True),
    'code': fields.Nested(HLACode, required=True),
    'second_code': fields.Nested(HLACode, required=False),
    'type': fields.Nested(HLAAntibodyTypeJson, required=True)
})

HLAAntibodyRaw = patient_api.model('HlaAntibodyRaw', {
    'raw_code': fields.String(required=True),
    'mfi': fields.Integer(required=True),
    'cutoff': fields.Integer(required=True)
})

AntibodiesPerGroup = patient_api.model('AntibodiesPerGroup', {
    'hla_group': fields.String(required=True, enum=[group.name for group in HLA_GROUPS]),
    'hla_antibody_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibody))
})

HLAAntibodies = patient_api.model('HlaAntibodies', {
    'hla_antibodies_raw_list': fields.List(required=True, cls_or_instance=fields.Nested(HLAAntibodyRaw)),
    'hla_antibodies_per_groups': fields.List(required=True,
                                             description='hla antibodies split to hla groups',
                                             example=HLA_ANTIBODIES_PER_GROUPS_EXAMPLE,
                                             cls_or_instance=fields.Nested(AntibodiesPerGroup)),
})
