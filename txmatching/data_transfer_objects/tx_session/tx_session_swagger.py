from flask_restx import fields

from txmatching.data_transfer_objects.patients.patient_swagger import (
    DONOR_MODEL, RECIPIENT_MODEL)
from txmatching.utils.country import Country
from txmatching.web.api.namespaces import tx_session_api

TX_SESSION_JSON_IN = tx_session_api.model("New Tx session", {
    "name": fields.String(required=True)
})

TX_SESSION_JSON_OUT = tx_session_api.model("New Tx session", {
    "name": fields.String(required=True),
    "db_id": fields.Integer(required=True),
})


UPLOAD_PATIENTS_JSON = tx_session_api.model(
    'Upload patients',
    {
        "country": fields.String(required=True, enum=[country.name for country in Country]),
        "tx_session_name": fields.String(required=True),
        # TODO remove country from DONOR_MODEL and RECIPIENT MODEL as it shall be defined globally above
        "donors": fields.List(required=True, cls_or_instance=fields.Nested(
            DONOR_MODEL
        )),
        "recipients": fields.List(required=True, cls_or_instance=fields.Nested(
            RECIPIENT_MODEL
        ))
    }
)
