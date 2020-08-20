from sqlalchemy import ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from kidney_exchange.database.db import db
from kidney_exchange.patients.patient import PatientType


class ConfigModel(db.Model):
    __tablename__ = 'config'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    parameters = db.Column(db.JSON, unique=False, nullable=False)
    created_by = db.Column(db.BIGINT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PairingResultModel(db.Model):
    __tablename__ = 'pairing_result'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    config_id = db.Column(db.BIGINT, unique=False, nullable=False)
    calculated_matchings = db.Column(db.JSON, unique=False, nullable=False)
    score_matrix = db.Column(db.JSON, unique=False, nullable=False)
    valid = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    patients = relationship('PairingResultPatientModel', backref='pairing_result')


class PairingResultPatientModel(db.Model):
    __tablename__ = 'pairing_result_patient'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    pairing_result_id = db.Column(db.BIGINT, ForeignKey('pairing_result.id'), unique=False, nullable=False)
    patient_id = db.Column(db.BIGINT, ForeignKey('patient.id'), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PatientModel(db.Model):
    __tablename__ = 'patient'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.TEXT, unique=False, nullable=False)
    patient_type = db.Column(db.Enum(PatientType), unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    hla_antigens = db.Column(db.JSON, unique=False, nullable=False)
    hla_antibodies = db.Column(db.JSON, unique=False, nullable=False)
    active = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    acceptable_blood = relationship('PatientAcceptableBloodModel', backref='patient')
    patient_pairs = relationship('PatientPairModel', backref='patient')
    patient_results = relationship('PairingResultPatientModel', backref='patient')


class PatientAcceptableBloodModel(db.Model):
    __tablename__ = 'patient_acceptable_blood'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    patient_id = db.Column(db.BIGINT, ForeignKey('patient.id'), unique=False, nullable=False)
    blood_type = db.Column(db.TEXT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PatientPairModel(db.Model):
    __tablename__ = 'patient_pair'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    recipient_id = db.Column(db.BIGINT, ForeignKey('patient.id'), unique=False, nullable=False)
    donor_id = db.Column(db.BIGINT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class AppUser(db.Model):
    __tablename__ = 'app_user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True)
    email = db.Column(db.TEXT, unique=True, nullable=False)
    pass_hash = db.Column(db.TEXT, unique=False, nullable=False)
    role = db.Column(db.TEXT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def __init__(self, email: str, pass_hash: str, role: str):
        self.email = email
        self.pass_hash = pass_hash
        self.role = role
        self._is_authenticated = False

    @staticmethod
    def is_active():
        return True

    def is_authenticated(self):
        return self._is_authenticated

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

    def set_authenticated(self, authenticated: bool):
        self._is_authenticated = authenticated


def modified_trigger(table_name):
    return f"""
CREATE TRIGGER trg_{table_name}_set_updated_at
BEFORE UPDATE ON {table_name}
FOR EACH ROW EXECUTE PROCEDURE set_updated_at())
"""


def created_trigger(table_name):
    return f"""
CREATE TRIGGER trg_{table_name}_set_created_at
BEFORE INSERT ON {table_name}
FOR EACH ROW EXECUTE PROCEDURE set_created_at())
"""


def create_modified_trigger(target, connection, **kwargs):
    """
    This is used to add bookkeeping triggers after a table is created. It hooks
    into the SQLAlchemy event system. It expects the target to be an instance of
    MetaData.
    """
    for key in target.tables:
        table = target.tables[key]
        connection.execute(modified_trigger(table.name))
        connection.execute(created_trigger(table.name))


Base = declarative_base()

event.listen(Base.metadata, 'after_create', create_modified_trigger)
