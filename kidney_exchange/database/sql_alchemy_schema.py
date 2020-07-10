from kidney_exchange.database.db import db


class ConfigModel(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    parameters = db.Column(db.JSON, unique=False, nullable=False)
    created_by = db.Column(db.BIGINT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PairingResultModel(db.Model):
    __tablename__ = 'pairing_result'

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    config_id = db.Column(db.BIGINT, unique=False, nullable=False)
    calculated_matchings = db.Column(db.JSON, unique=False, nullable=False)
    score_matrix = db.Column(db.JSON, unique=False, nullable=False)
    valid = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PairingResultPatientModel(db.Model):
    __tablename__ = 'pairing_result_patient'

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    pairing_result_id = db.Column(db.BIGINT, unique=False, nullable=False)
    patient_id = db.Column(db.BIGINT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PatientModel(db.Model):
    __tablename__ = 'patient'

    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.TEXT, unique=False, nullable=False)
    patient_type = db.Column(db.TEXT, unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    typization = db.Column(db.JSON, unique=False, nullable=False)
    luminex = db.Column(db.JSON, unique=False, nullable=False)
    acceptable_blood = db.Column(db.JSON, unique=False, nullable=False)
    active = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class PatientPairModel(db.Model):
    __tablename__ = 'patient_pair'
    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    recipient_id = db.Column(db.BIGINT, unique=False, nullable=False)
    donor_id = db.Column(db.BIGINT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
