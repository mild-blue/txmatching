import unittest

from flask import Flask

from kidney_exchange.config.configuration import Configuration, DonorRecipientScore
from kidney_exchange.database.db import db
from kidney_exchange.database.services.config_service import save_configuration_as_current
from kidney_exchange.solve_service.solve_from_db import solve_from_db


class DbTests(unittest.TestCase):

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """

        self.app = Flask(__name__)
        db.init_app(self.app)
        self.app.app_context().push()
        with self.app.app_context():
            print(db.create_all())

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with self.app.app_context():
            db.drop_all()


class TestSaveAndGetConfiguration(DbTests):

    def test_solve_from_db(self):
        # with app.app_context():
        configuration = Configuration(
            manual_donor_recipient_scores=[
                DonorRecipientScore(donor_id=1, recipient_id=4, score=1.0)],
            require_new_donor_having_better_match_in_compatibility_index=False)
        save_configuration_as_current(configuration)
        self.assertEqual(1, len(list(solve_from_db())))
