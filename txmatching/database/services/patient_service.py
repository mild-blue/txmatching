import dataclasses
import logging
from typing import List, Optional, Tuple, Union

import dacite
from sqlalchemy import and_

from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorExcelDTO
from txmatching.data_transfer_objects.patients.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientExcelDTO
from txmatching.data_transfer_objects.patients.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import \
    get_newest_txm_event_db_id
from txmatching.database.sql_alchemy_schema import (
    ConfigModel, DonorModel, RecipientAcceptableBloodModel,
    RecipientHLAAntibodyModel, RecipientModel, TxmEventModel)
from txmatching.patients.patient import (Donor, DonorType, Patient, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntibody,
                                                    HLATyping,
                                                    PatientParameters)
from txmatching.utils.hla_system.hla_table import parse_code

logger = logging.getLogger(__name__)


def donor_excel_dto_to_donor_model(donor: DonorExcelDTO,
                                   recipient: Optional[RecipientModel],
                                   txm_event_db_id: int) -> DonorModel:
    maybe_recipient_id = recipient.id if recipient else None
    donor_type = DonorType.DONOR if recipient else DonorType.ALTRUIST
    donor_model = DonorModel(
        medical_id=donor.medical_id,
        country=donor.parameters.country_code,
        blood=donor.parameters.blood_group,
        hla_typing=dataclasses.asdict(donor.parameters.hla_typing),
        active=True,
        recipient_id=maybe_recipient_id,
        donor_type=donor_type,
        txm_event_id=txm_event_db_id
    )
    return donor_model


def recipient_excel_dto_to_recipient_model(recipient_excel_dto: RecipientExcelDTO,
                                           txm_event_db_id: int) -> RecipientModel:
    patient_model = RecipientModel(
        medical_id=recipient_excel_dto.medical_id,
        country=recipient_excel_dto.parameters.country_code,
        blood=recipient_excel_dto.parameters.blood_group,
        hla_typing=dataclasses.asdict(recipient_excel_dto.parameters.hla_typing),
        hla_antibodies=[RecipientHLAAntibodyModel(
            raw_code=hla_antibody.raw_code,
            code=hla_antibody.code,
            cutoff=hla_antibody.cutoff,
            mfi=hla_antibody.mfi
        ) for hla_antibody in recipient_excel_dto.hla_antibodies.hla_antibodies_list],
        active=True,
        acceptable_blood=[RecipientAcceptableBloodModel(blood_type=blood)
                          for blood in recipient_excel_dto.acceptable_blood_groups],
        txm_event_id=txm_event_db_id,
        recipient_cutoff=recipient_excel_dto.recipient_cutoff
    )
    return patient_model


def save_patients_from_excel_to_empty_txm_event(donors_recipients: Tuple[List[DonorExcelDTO], List[RecipientExcelDTO]],
                                                txm_event_db_id: int):
    txm_event = get_txm_event(txm_event_db_id)
    if len(txm_event.donors_dict) > 0 or len(txm_event.recipients_dict) > 0:
        raise ValueError('Txm event not empty, cannot send patients to database')

    maybe_recipient_models = [recipient_excel_dto_to_recipient_model(recipient, txm_event_db_id)
                              if recipient else None for recipient in donors_recipients[1]]
    recipient_models = [recipient_model for recipient_model in maybe_recipient_models if recipient_model]
    db.session.add_all(recipient_models)
    db.session.commit()

    donor_models = [donor_excel_dto_to_donor_model(donor_dto, maybe_recipient_model, txm_event_db_id) for
                    donor_dto, maybe_recipient_model in zip(donors_recipients[0], maybe_recipient_models)]
    db.session.add_all(donor_models)
    db.session.commit()


def _get_base_patient_from_patient_model(patient_model: Union[DonorModel, RecipientModel]) -> Patient:
    return Patient(
        db_id=patient_model.id,
        medical_id=patient_model.medical_id,
        parameters=PatientParameters(
            blood_group=patient_model.blood,
            country_code=patient_model.country,
            hla_typing=dacite.from_dict(data_class=HLATyping, data=patient_model.hla_typing),
            height=patient_model.height,
            weight=patient_model.weight,
            yob=patient_model.yob,
            sex=patient_model.sex
        ))


def _get_donor_from_donor_model(donor_model: DonorModel) -> Donor:
    base_patient = _get_base_patient_from_patient_model(donor_model)

    return Donor(base_patient.db_id,
                 base_patient.medical_id,
                 parameters=base_patient.parameters,
                 donor_type=donor_model.donor_type,
                 related_recipient_db_id=donor_model.recipient_id
                 )


def _get_recipient_from_recipient_model(recipient_model: RecipientModel,
                                        related_donor_db_id: Optional[int] = None) -> Recipient:
    if not related_donor_db_id:
        related_donor_db_id = DonorModel.query.filter(DonorModel.recipient_id == recipient_model.id).one().id
    base_patient = _get_base_patient_from_patient_model(recipient_model)

    return Recipient(base_patient.db_id,
                     base_patient.medical_id,
                     parameters=base_patient.parameters,
                     related_donor_db_id=related_donor_db_id,
                     hla_antibodies=HLAAntibodies(
                         [HLAAntibody(code=hla_antibody.code,
                                      mfi=hla_antibody.mfi,
                                      cutoff=hla_antibody.cutoff,
                                      raw_code=hla_antibody.raw_code)
                          for hla_antibody in recipient_model.hla_antibodies]
                     ),
                     acceptable_blood_groups=[acceptable_blood_model.blood_type for acceptable_blood_model in
                                              recipient_model.acceptable_blood],
                     recipient_cutoff=recipient_model.recipient_cutoff,
                     recipient_requirements=RecipientRequirements(**recipient_model.recipient_requirements),
                     waiting_since=recipient_model.waiting_since,
                     previous_transplants=recipient_model.previous_transplants
                     )


def update_recipient(recipient_update_dto: RecipientUpdateDTO) -> Recipient:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    old_recipient_model = RecipientModel.query.get(recipient_update_dto.db_id)
    txm_event_db_id = old_recipient_model.txm_event_id
    ConfigModel.query.filter(
        and_(ConfigModel.id > 0, ConfigModel.txm_event_id == txm_event_db_id)).delete()

    recipient_update_dict = {}
    if recipient_update_dto.acceptable_blood_groups:
        acceptable_blood_models = [
            RecipientAcceptableBloodModel(blood_type=blood, recipient_id=recipient_update_dto.db_id) for blood
            in
            recipient_update_dto.acceptable_blood_groups]
        RecipientAcceptableBloodModel.query.filter(
            RecipientAcceptableBloodModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(acceptable_blood_models)
    if recipient_update_dto.hla_antibodies:
        # not the best approach: in case cutoff was different per antibody before it will be unified now, but
        # but good for the moment
        old_recipient = _get_recipient_from_recipient_model(old_recipient_model)
        cutoff = recipient_update_dto.cutoff if recipient_update_dto.cutoff is not None \
            else old_recipient.recipient_cutoff

        hla_antibodies = [
            RecipientHLAAntibodyModel(recipient_id=recipient_update_dto.db_id,
                                      raw_code=hla_antibody_dto.raw_code,
                                      mfi=hla_antibody_dto.mfi,
                                      cutoff=cutoff,
                                      code=parse_code(hla_antibody_dto.raw_code)) for hla_antibody_dto
            in
            recipient_update_dto.hla_antibodies.hla_antibodies_list]

        RecipientHLAAntibodyModel.query.filter(
            RecipientHLAAntibodyModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(hla_antibodies)
    if recipient_update_dto.hla_typing:
        recipient_update_dict['hla_typing'] = dataclasses.asdict(recipient_update_dto.hla_typing)
    if recipient_update_dto.recipient_requirements:
        recipient_update_dict['recipient_requirements'] = dataclasses.asdict(
            recipient_update_dto.recipient_requirements)
    if recipient_update_dto.cutoff:
        recipient_update_dict['recipient_cutoff'] = recipient_update_dto.cutoff

    RecipientModel.query.filter(RecipientModel.id == recipient_update_dto.db_id).update(recipient_update_dict)
    db.session.commit()
    return _get_recipient_from_recipient_model(RecipientModel.query.get(recipient_update_dto.db_id))


def update_donor(donor_update_dto: DonorUpdateDTO) -> Donor:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    old_donor = DonorModel.query.get(donor_update_dto.db_id)
    ConfigModel.query.filter(
        and_(ConfigModel.id > 0, ConfigModel.txm_event_id == old_donor.txm_event_id)).delete()

    donor_update_dict = {}
    if donor_update_dto.hla_typing:
        donor_update_dict['hla_typing'] = dataclasses.asdict(donor_update_dto.hla_typing)
    DonorModel.query.filter(DonorModel.id == donor_update_dto.db_id).update(donor_update_dict)
    db.session.commit()
    return _get_donor_from_donor_model(DonorModel.query.get(donor_update_dto.db_id))


def get_txm_event(txm_event_db_id: Optional[int] = None) -> TxmEvent:
    if not txm_event_db_id:
        txm_event_db_id = get_newest_txm_event_db_id()
    txm_event_model = TxmEventModel.query.get(txm_event_db_id)

    active_donors = txm_event_model.donors
    active_recipients = txm_event_model.recipients
    donors_with_recipients = [(donor_model.recipient_id, _get_donor_from_donor_model(donor_model))
                              for donor_model in active_donors]

    donors_dict = {donor.db_id: donor for _, donor in donors_with_recipients}
    donors_with_recipients_dict = {related_recipient_id: donor.db_id for related_recipient_id, donor in
                                   donors_with_recipients if related_recipient_id}

    recipients_dict = {
        recipient_model.id: _get_recipient_from_recipient_model(
            recipient_model, donors_with_recipients_dict[recipient_model.id])
        for recipient_model in active_recipients}

    return TxmEvent(db_id=txm_event_model.id, name=txm_event_model.name, donors_dict=donors_dict,
                    recipients_dict=recipients_dict)
