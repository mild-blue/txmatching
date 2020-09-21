from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app import DbTests
from txmatching.database.services.patient_service import get_txm_event
from txmatching.database.services.txm_event_service import create_txm_event, \
    get_newest_txm_event_db_id
from txmatching.database.sql_alchemy_schema import ConfigModel, RecipientModel, PairingResultModel
from txmatching.web import report_api, REPORTS_NAMESPACE


class TestMatchingApi(DbTests):

    def test_txm_event_creation_and_deletion(self):
        self.fill_db_with_patients_and_results()
        self.api.add_namespace(report_api, path=f'/{REPORTS_NAMESPACE}')
        txm_event_db_id = get_newest_txm_event_db_id()
        txm_event = get_txm_event(txm_event_db_id)
        configs = ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()
        self.assertEqual(2, len(txm_event.donors_dict))
        self.assertEqual(2, len(configs))
        self.assertEqual(1, len(PairingResultModel.query.filter(PairingResultModel.config_id.in_(
            [config.id for config in configs])).all()))
        with self.assertRaises(ValueError):
            create_txm_event('test')
        txm_event = create_or_overwrite_txm_event('test')
        self.assertEqual('test', txm_event.name)
        self.assertEqual(0, len(RecipientModel.query.filter(RecipientModel.txm_event_id == txm_event.db_id).all()))
        self.assertEqual(0, len(ConfigModel.query.filter(ConfigModel.txm_event_id == txm_event.db_id).all()))
