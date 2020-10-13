import dataclasses

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from txmatching.auth.data_types import UserRole
from txmatching.database.db import db
from txmatching.patients.patient import DonorType, RecipientRequirements
# pylint: disable=too-few-public-methods,too-many-arguments
# disable because sqlalchemy needs classes without public methods
from txmatching.utils.enums import Country, Sex


class ConfigModel(db.Model):
    __tablename__ = 'config'
    __table_args__ = {'extend_existing': True}
    # Here and below I am using Integer instead of BigInt because it seems that there is a bug and BigInteger is not
    # transferred to BigSerial with autoincrement True, but to BigInt only.
    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id'), unique=False, nullable=False)
    parameters = db.Column(db.JSON, unique=False, nullable=False)
    created_by = db.Column(db.Integer, unique=False, nullable=False)
    # created at and updated at is not handled by triggers as then am not sure how tests would work, as triggers
    # seem to be specific as per db and I do not think its worth the effort as this simple approach works fine
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    pairing_results = relationship('PairingResultModel', backref='config', cascade='all, delete')


class PairingResultModel(db.Model):
    __tablename__ = 'pairing_result'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    config_id = db.Column(db.Integer, ForeignKey('config.id'), unique=False, nullable=False)
    calculated_matchings = db.Column(db.JSON, unique=False, nullable=False)
    score_matrix = db.Column(db.JSON, unique=False, nullable=False)
    valid = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class TxmEventModel(db.Model):
    __tablename__ = 'txm_event'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.TEXT, unique=True, nullable=False)
    configs = relationship('ConfigModel', backref='txm_event', cascade='all, delete')
    donors = relationship('DonorModel', backref='txm_event', cascade='all, delete')
    recipients = relationship('RecipientModel', backref='txm_event', cascade='all, delete')
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class RecipientModel(db.Model):
    __tablename__ = 'recipient'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id'), unique=False, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.Enum(Country), unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    hla_typing = db.Column(db.JSON, unique=False, nullable=False)  # HLATyping is model of the JSON
    active = db.Column(db.BOOLEAN, unique=False, nullable=False)
    recipient_requirements = db.Column(db.JSON, unique=False, nullable=False,
                                       default=dataclasses.asdict(RecipientRequirements()))
    recipient_cutoff = db.Column(db.Integer, unique=False, nullable=False)
    sex = db.Column(db.Enum(Sex), unique=False, nullable=True)
    height = db.Column(db.Integer, unique=False, nullable=True)
    weight = db.Column(db.Float, unique=False, nullable=True)
    yob = db.Column(db.Integer, unique=False, nullable=True)
    waiting_since = db.Column(db.DateTime(timezone=True), unique=False, nullable=True)
    previous_transplants = db.Column(db.Integer, unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    acceptable_blood = relationship('RecipientAcceptableBloodModel', backref='recipient', cascade='all, delete')
    hla_antibodies = relationship('RecipientHLAAntibodyModel', backref='recipient', cascade='all, delete')
    UniqueConstraint('medical_id', 'txm_event_id')


class DonorModel(db.Model):
    __tablename__ = 'donor'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id'), unique=False, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.Enum(Country), unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    hla_typing = db.Column(db.JSON, unique=False, nullable=False)
    active = db.Column(db.BOOLEAN, unique=False, nullable=False)
    donor_type = db.Column(db.Enum(DonorType), unique=False, nullable=False)
    sex = db.Column(db.Enum(Sex), unique=False, nullable=True)
    height = db.Column(db.Integer, unique=False, nullable=True)
    weight = db.Column(db.Float, unique=False, nullable=True)
    yob = db.Column(db.Integer, unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    recipient_id = db.Column(db.Integer, ForeignKey('recipient.id'), unique=False, nullable=True)
    recipient = relationship('RecipientModel', backref=backref('recipient', uselist=False))
    UniqueConstraint('medical_id', 'txm_event_id')


class RecipientAcceptableBloodModel(db.Model):
    __tablename__ = 'recipient_acceptable_blood'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    recipient_id = db.Column(db.Integer, ForeignKey('recipient.id'), unique=False, nullable=False)
    blood_type = db.Column(db.TEXT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class RecipientHLAAntibodyModel(db.Model):
    __tablename__ = 'recipient_hla_antibodies'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    recipient_id = db.Column(db.Integer, ForeignKey('recipient.id'), unique=False, nullable=False)
    raw_code = db.Column(db.TEXT, unique=False, nullable=False)
    mfi = db.Column(db.Integer, unique=False, nullable=False)
    cutoff = db.Column(db.Integer, unique=False, nullable=False)
    code = db.Column(db.TEXT, unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class AppUserModel(db.Model):
    __tablename__ = 'app_user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.TEXT, unique=True, nullable=False)
    pass_hash = db.Column(db.TEXT, unique=False, nullable=False)
    role = db.Column(db.Enum(UserRole), unique=False, nullable=False)
    default_txm_event_id = db.Column(db.Integer, unique=False, nullable=True)
    # Whitelisted IP address if role is SERVICE
    # Seed for TOTP in all other cases
    second_factor_material = db.Column(db.TEXT, unique=False, nullable=False)
    phone_number = db.Column(db.TEXT, unique=False, nullable=True, default=None)
    require_2fa = db.Column(db.BOOLEAN, unique=False, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class UploadedDataModel(db.Model):
    __tablename__ = 'uploaded_data'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id'), unique=False, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('app_user.id'), unique=False, nullable=False)
    uploaded_data = db.Column(db.JSON, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now(),
                           onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
