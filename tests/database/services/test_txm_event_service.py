from local_testing_utilities.populate_db import (ADMIN_USER, SERVICE_USER,
                                                 VIEWER_USER)
from local_testing_utilities.utils import create_or_overwrite_txm_event
from tests.test_utilities.prepare_app_for_tests import DbTests
from txmatching.auth.exceptions import UnauthorizedException
from txmatching.database.services.app_user_management import get_app_user_by_id
from txmatching.database.services.txm_event_service import (
    get_allowed_txm_event_ids_for_current_user,
    get_txm_event_id_for_current_user, set_allowed_txm_event_ids_for_user,
    update_default_txm_event_id_for_current_user)

TXM_EVENT_NAME_1 = 'txm_event_1'
TXM_EVENT_NAME_2 = 'txm_event_2'
TXM_EVENT_NAME_3 = 'txm_event_3'


class TestTxmEventService(DbTests):

    def test_set_allowed_txm_event_ids_for_different_users(self):
        txm_event_1 = create_or_overwrite_txm_event(TXM_EVENT_NAME_1)
        txm_event_2 = create_or_overwrite_txm_event(TXM_EVENT_NAME_2)
        txm_event_3 = create_or_overwrite_txm_event(TXM_EVENT_NAME_3)

        admin_user = get_app_user_by_id(ADMIN_USER['id'])
        viewer_user = get_app_user_by_id(VIEWER_USER['id'])
        service_user = get_app_user_by_id(SERVICE_USER['id'])

        # Admin has all txm events as allowed by default
        self.login_with_credentials(ADMIN_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_1.db_id, txm_event_2.db_id, txm_event_3.db_id])

        # Viewer has no txm events as allowed by default
        self.login_with_credentials(VIEWER_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [])

        # Service user has no txm events as allowed by default
        self.login_with_credentials(SERVICE_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [])

        # Try to change allowed txm events for all users
        set_allowed_txm_event_ids_for_user(admin_user, [txm_event_1.db_id])
        set_allowed_txm_event_ids_for_user(viewer_user, [txm_event_2.db_id])
        set_allowed_txm_event_ids_for_user(service_user, [txm_event_3.db_id])

        # Admin allowed txm events are not affected
        self.login_with_credentials(ADMIN_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_1.db_id, txm_event_2.db_id, txm_event_3.db_id])

        # Viewer allowed txm events chaged properly
        self.login_with_credentials(VIEWER_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_2.db_id])

        # Service user allowed txm events chaged properly
        self.login_with_credentials(SERVICE_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_3.db_id])

        # Change allowed txm events again
        set_allowed_txm_event_ids_for_user(viewer_user, [txm_event_1.db_id])
        set_allowed_txm_event_ids_for_user(service_user, [txm_event_2.db_id])

        # Viewer allowed txm events chaged properly (previous allowed event is removed)
        self.login_with_credentials(VIEWER_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_1.db_id])

        # Service user allowed txm events chaged properly (previous allowed event is removed)
        self.login_with_credentials(SERVICE_USER)
        event_ids = get_allowed_txm_event_ids_for_current_user()
        self.assertCountEqual(event_ids, [txm_event_2.db_id])

    def test_get_default_txm_event(self):
        txm_event_1 = create_or_overwrite_txm_event(TXM_EVENT_NAME_1)
        txm_event_2 = create_or_overwrite_txm_event(TXM_EVENT_NAME_2)
        txm_event_3 = create_or_overwrite_txm_event(TXM_EVENT_NAME_3)

        viewer_user = get_app_user_by_id(VIEWER_USER['id'])
        self.login_with_credentials(VIEWER_USER)

        # Allow events 1, 2
        set_allowed_txm_event_ids_for_user(viewer_user, [txm_event_1.db_id, txm_event_2.db_id])

        # Set event 1 as default
        update_default_txm_event_id_for_current_user(txm_event_1.db_id)

        # Event 1 is returned as default
        self.assertEqual(get_txm_event_id_for_current_user(), txm_event_1.db_id)

        # Set event 3 as default raises error because it is not in allowed events
        with self.assertRaises(UnauthorizedException):
            update_default_txm_event_id_for_current_user(txm_event_3.db_id)

        # Allow events 2, 3
        set_allowed_txm_event_ids_for_user(viewer_user, [txm_event_2.db_id, txm_event_3.db_id])

        # Event 3 is returned as default
        self.assertEqual(get_txm_event_id_for_current_user(), txm_event_3.db_id)

        # And default event is changed to 3 in db
        viewer_user = get_app_user_by_id(VIEWER_USER['id'])
        self.assertEqual(viewer_user.default_txm_event_id, txm_event_3.db_id)

        # Allow event 2 only
        set_allowed_txm_event_ids_for_user(viewer_user, [txm_event_2.db_id])

        # Event 2 is returned as default
        self.assertEqual(get_txm_event_id_for_current_user(), txm_event_2.db_id)

        # And default event is changed to 2 in db
        viewer_user = get_app_user_by_id(VIEWER_USER['id'])
        self.assertEqual(viewer_user.default_txm_event_id, txm_event_2.db_id)

        # Allow no event
        set_allowed_txm_event_ids_for_user(viewer_user, [])

        # Error is raised when trying to get default event
        self.assertEqual(viewer_user.default_txm_event_id, txm_event_2.db_id)
        with self.assertRaises(UnauthorizedException):
            get_txm_event_id_for_current_user()

        # Default event is changed to null in db
        viewer_user = get_app_user_by_id(VIEWER_USER['id'])
        self.assertEqual(viewer_user.default_txm_event_id, None)
