import unittest

from flask import Flask

from txmatching.database.db import db
from txmatching.database.services.patient_service import save_patients
from txmatching.solve_service.solve_from_db import solve_from_db
from txmatching.utils.excel_parsing.parse_excel_data import parse_excel_data


class DbTests(unittest.TestCase):

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """

        self.app = Flask(__name__)
        db.init_app(self.app)
        self.app.app_context().push()

        db.create_all()
        patients = parse_excel_data("test_utilities/data.xlsx")
        save_patients(patients)

        solve_from_db()

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with self.app.app_context():
            db.drop_all()
