import dataclasses
from typing import List

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from txmatching.auth.data_types import UserRole
from txmatching.database.db import db
from txmatching.patients.patient import DonorType, RecipientRequirements
from txmatching.utils.country_enum import Country
# pylint: disable=too-few-public-methods,too-many-arguments
# disable because sqlalchemy needs classes without public methods
from txmatching.utils.enums import Sex
from txmatching.utils.hla_system.hla_code_processing_result_detail import \
    HlaCodeProcessingResultDetail


class ConfigModel(db.Model):
    __tablename__ = 'config'
    __table_args__ = {'extend_existing': True}
    # Here and below I am using Integer instead of BigInt because it seems that there is a bug and BigInteger is not
    # transferred to BigSerial with autoincrement True, but to BigInt only.
    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id', ondelete='CASCADE'), unique=False, nullable=False)
    parameters = db.Column(db.JSON, unique=False, nullable=False)
    patients_hash = db.Column(db.BigInteger, unique=False, nullable=False)
    created_by = db.Column(db.Integer, unique=False, nullable=False)
    # created at and updated at is not handled by triggers as then am not sure how tests would work, as triggers
    # seem to be specific as per db and I do not think its worth the effort as this simple approach works fine
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    pairing_results = db.relationship('PairingResultModel', backref='config', passive_deletes=True)
    UniqueConstraint('txm_event_id')


class PairingResultModel(db.Model):
    __tablename__ = 'pairing_result'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    config_id = db.Column(db.Integer, ForeignKey('config.id', ondelete='CASCADE'), unique=False, nullable=False)
    calculated_matchings = db.Column(db.JSON, unique=False, nullable=False)
    score_matrix = db.Column(db.JSON, unique=False, nullable=False)
    valid = db.Column(db.BOOLEAN, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    UniqueConstraint('config_id')


class TxmEventModel(db.Model):
    __tablename__ = 'txm_event'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.TEXT, unique=True, nullable=False)
    configs = db.relationship('ConfigModel', backref='txm_event', passive_deletes=True)  # type: List[ConfigModel]
    donors = db.relationship('DonorModel', backref='txm_event', passive_deletes=True)  # type: List[DonorModel]
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class RecipientModel(db.Model):
    __tablename__ = 'recipient'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id', ondelete='CASCADE'), unique=False, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.Enum(Country), unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    hla_typing_raw = db.Column(db.JSON, unique=False, nullable=False)
    hla_typing = db.Column(db.JSON, unique=False, nullable=False)  # HLATyping is model of the JSON
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
    acceptable_blood = db.relationship('RecipientAcceptableBloodModel', backref='recipient', passive_deletes=True,
                                       lazy='joined')  # type: List[RecipientAcceptableBloodModel]
    hla_antibodies = db.Column(db.JSON, unique=False, nullable=False)
    hla_antibodies_raw = db.relationship('HLAAntibodyRawModel', backref='recipient', passive_deletes=True,
                                         lazy='joined')  # type: List[HLAAntibodyRawModel]
    UniqueConstraint('medical_id', 'txm_event_id')

    def __repr__(self):
        return f'<RecipientModel {self.id} (medical_id={self.medical_id})>'


class DonorModel(db.Model):
    __tablename__ = 'donor'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id', ondelete='CASCADE'), unique=False, nullable=False)
    medical_id = db.Column(db.TEXT, unique=False, nullable=False)
    country = db.Column(db.Enum(Country), unique=False, nullable=False)
    blood = db.Column(db.TEXT, unique=False, nullable=False)
    hla_typing_raw = db.Column(db.JSON, unique=False, nullable=False)
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
    recipient = db.relationship('RecipientModel', backref=backref('donor', uselist=False),
                                passive_deletes=True,
                                lazy='joined')
    UniqueConstraint('medical_id', 'txm_event_id')

    def __repr__(self):
        return f'<DonorModel {self.id} (medical_id={self.medical_id})>'


class RecipientAcceptableBloodModel(db.Model):
    __tablename__ = 'recipient_acceptable_blood'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    recipient_id = db.Column(db.Integer, ForeignKey('recipient.id', ondelete='CASCADE'), unique=False, nullable=False)
    blood_type = db.Column(db.TEXT, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class HLAAntibodyRawModel(db.Model):
    __tablename__ = 'hla_antibody_raw'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    recipient_id = db.Column(db.Integer, ForeignKey('recipient.id', ondelete='CASCADE'), unique=False, nullable=False)
    raw_code = db.Column(db.TEXT, unique=False, nullable=False)
    mfi = db.Column(db.Integer, unique=False, nullable=False)
    cutoff = db.Column(db.Integer, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f'<HLAAntibodyRawModel {self.id} ' \
               f'(raw_code={self.raw_code}, mfi={self.mfi}, cutoff={self.cutoff})>'


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
    allowed_edit_countries = db.Column(db.JSON, unique=False, nullable=False, default=lambda: [])

    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class UserToAllowedEvent(db.Model):
    __tablename__ = 'user_to_allowed_event'
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(
        db.Integer,
        ForeignKey('app_user.id', ondelete='CASCADE'),
        unique=False, nullable=False, primary_key=True, index=True
    )
    txm_event_id = db.Column(
        db.Integer,
        ForeignKey('txm_event.id', ondelete='CASCADE'),
        unique=False, nullable=False, primary_key=True, index=True
    )


class UploadedDataModel(db.Model):
    __tablename__ = 'uploaded_data'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id', ondelete='CASCADE'), unique=False, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('app_user.id'), unique=False, nullable=False)
    uploaded_data = db.Column(db.JSON, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now(),
                           onupdate=func.now())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class ParsingErrorModel(db.Model):
    __tablename__ = 'parsing_error'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    hla_code = db.Column(db.TEXT, unique=False, nullable=False)
    hla_code_processing_result_detail = db.Column(db.Enum(HlaCodeProcessingResultDetail), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        unique=False,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)


class UploadedFileModel(db.Model):
    __tablename__ = 'uploaded_file'
    __table_args__ = {'extend_existing': True}

    id = db.Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    file_name = db.Column(db.TEXT, unique=False, nullable=False)
    file = db.Column(db.LargeBinary, unique=False, nullable=False)
    txm_event_id = db.Column(db.Integer, ForeignKey('txm_event.id', ondelete='CASCADE'), unique=False, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('app_user.id', ondelete='CASCADE'), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True),
        unique=False,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
