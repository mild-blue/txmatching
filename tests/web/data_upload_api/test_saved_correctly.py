from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from tests.web.data_upload_api.patient_upload_example_data import (
    TXM_EVENT_NAME, VALID_UPLOAD_1)
from txmatching.auth.data_types import UserRole
from txmatching.database.services.patient_service import get_txm_event
from txmatching.patients.patient_parameters import HLAType, HLATyping
from txmatching.web import (PATIENT_NAMESPACE, TXM_EVENT_NAMESPACE,
                            patient_api, txm_event_api)


class TestMatchingApi(DbTests):

    def test_saved(self):
        self.api.add_namespace(txm_event_api, path=f'/{TXM_EVENT_NAMESPACE}')
        self.api.add_namespace(patient_api, path=f'/{PATIENT_NAMESPACE}')
        txm_event = create_or_overwrite_txm_event(name=TXM_EVENT_NAME)
        self.login_with_role(UserRole.SERVICE)
        with self.app.test_client() as client:
            client.put(
                f'/{TXM_EVENT_NAMESPACE}/patients',
                headers=self.auth_headers,
                json=VALID_UPLOAD_1
            )
        self.assertEqual(HLATyping(hla_types_list=[HLAType(raw_code='A2', code='A2')]),
                         get_txm_event(txm_event.db_id).donors_dict[1].parameters.hla_typing)
