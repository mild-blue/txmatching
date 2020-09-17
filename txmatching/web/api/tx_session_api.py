# pylint: disable=no-self-use
# can not, they are used for generating swagger which needs class

import logging

from flask_restx import Resource, fields

from txmatching.auth.login_check import login_required
from txmatching.data_transfer_objects.tx_session.tx_session_swagger import (
    TX_SESSION_JSON_IN, TX_SESSION_JSON_OUT, UPLOAD_PATIENTS_JSON)
from txmatching.web.api.namespaces import tx_session_api

logger = logging.getLogger(__name__)


TX_SESSION_FAIL_RESPONSE = tx_session_api.model('Tx session FailResponse', {
    'error': fields.String(required=True),
})


# pylint: disable=no-self-use
# the methods here need self due to the annotations
@tx_session_api.route('/tx_session', methods=['POST'])
class TxSessionApi(Resource):

    @tx_session_api.doc(body=TX_SESSION_JSON_IN, security='bearer',
                        description='Endpoint that lets an ADMIN to create a new tx session with provided name')
    @tx_session_api.response(code=200, model=TX_SESSION_JSON_OUT,
                             description='Returns the newly created tx session object')
    @tx_session_api.response(code=500, model=TX_SESSION_FAIL_RESPONSE, description='')
    @login_required()
    def post(self):
        pass


@tx_session_api.route('/upload_patients', methods=['PUT'])
class TxSessionUploadPatients(Resource):

    @tx_session_api.doc(body=UPLOAD_PATIENTS_JSON, security='bearer', description="""
    Endpoint that lets user with rights to given country to upload patient data for given tx session.
    The enpoints deletes all patients from respective country in case there were any.""".replace(r' +', ' '))
    @tx_session_api.response(code=200, description='Success')
    @tx_session_api.response(code=500, description='Fail')
    # TODO validate based on country of the user https://trello.com/c/8tzYR2Dj
    @login_required()
    def put(self):
        # TODO add here the logic that will update patients https://trello.com/c/Yj70es9D
        pass
