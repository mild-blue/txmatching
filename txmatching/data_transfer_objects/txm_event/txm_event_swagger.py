from flask_restx import fields

from txmatching.data_transfer_objects.enums_swagger import (CountryCodeJson,
                                                            StrictnessTypeEnumJson,
                                                            TxmEventStateJson)
from txmatching.data_transfer_objects.hla.parsing_issue_swagger import \
    ParsingIssueJson
from txmatching.web.web_utils.namespaces import txm_event_api

TxmEventJsonIn = txm_event_api.model('NewTxmEvent', {
    'name': fields.String(required=True),
    'strictness_type': fields.Nested(StrictnessTypeEnumJson, required=False)
})

TxmDefaultEventJsonIn = txm_event_api.model('DefaultTxmEvent', {
    'id': fields.Integer(required=True)
})

TxmEventJsonOut = txm_event_api.model('TxmEvent', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'default_config_id': fields.Integer(required=False),
    'state': fields.Nested(TxmEventStateJson, required=True),
    'strictness_type': fields.Nested(StrictnessTypeEnumJson, required=True)
})

PatientsRecomputeParsingSuccessJson = txm_event_api.model('PatientsRecomputeParsingSuccess', {
    'patients_checked_antigens': fields.Integer(required=True),
    'patients_changed_antigens': fields.Integer(required=True),
    'patients_checked_antibodies': fields.Integer(required=True),
    'patients_changed_antibodies': fields.Integer(required=True),
    'parsing_issues': fields.List(required=True, cls_or_instance=fields.Nested(ParsingIssueJson)),
})

TxmEventsJson = txm_event_api.model('TxmEvents', {
    'events': fields.List(required=True, cls_or_instance=fields.Nested(
        TxmEventJsonOut
    )),
})

TxmEventUpdateJsonIn = txm_event_api.model('TxmEventUpdateIn', {
    'state': fields.Nested(TxmEventStateJson, required=False),
})

TxmEventExportJsonIn = txm_event_api.model('TxmEventExport', {
    'country': fields.Nested(CountryCodeJson, required=True),
    'new_txm_event_name': fields.String(required=True)
})

TxmEventCopyPatientsJsonIn = txm_event_api.model('TxmEventCopy', {
    'txm_event_id_from': fields.Integer(required=True),
    'txm_event_id_to': fields.Integer(required=True),
    'donor_ids': fields.List(required=True, cls_or_instance=fields.Integer),
})
