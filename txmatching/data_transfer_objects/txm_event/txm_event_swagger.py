from flask_restx import fields

from txmatching.web.web_utils.namespaces import txm_event_api

TxmEventJsonIn = txm_event_api.model('NewTxmEvent', {
    'name': fields.String(required=True)
})

TxmDefaultEventJsonIn = txm_event_api.model('DefaultTxmEvent', {
    'id': fields.Integer(required=True)
})

TxmEventJsonOut = txm_event_api.model('TxmEvent', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'default_config_id': fields.Integer(required=False),
})

PatientsRecomputeParsingSuccessJson = txm_event_api.model('PatientsRecomputeParsingSuccess', {
    'patients_checked_antigens': fields.Integer(required=True),
    'patients_changed_antigens': fields.Integer(required=True),
    'patients_checked_antibodies': fields.Integer(required=True),
    'patients_changed_antibodies': fields.Integer(required=True),
    'parsing_errors': fields.List(required=True, cls_or_instance=fields.Raw()),
})

TxmEventsJson = txm_event_api.model('TxmEvents', {
    'events': fields.List(required=True, cls_or_instance=fields.Nested(
        TxmEventJsonOut
    )),
})
