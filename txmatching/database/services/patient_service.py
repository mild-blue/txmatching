import collections
import dataclasses
import datetime
import logging
from typing import List, Optional, Tuple, Union

import dacite
from sqlalchemy import and_

from txmatching.auth.exceptions import InvalidArgumentException
from txmatching.data_transfer_objects.patients.donor_excel_dto import \
    DonorExcelDTO
from txmatching.data_transfer_objects.patients.patient_parameters_dto import \
    HLATypingDTO
from txmatching.data_transfer_objects.patients.recipient_excel_dto import \
    RecipientExcelDTO
from txmatching.data_transfer_objects.patients.update_dtos.donor_update_dto import \
    DonorUpdateDTO
from txmatching.data_transfer_objects.patients.update_dtos.recipient_update_dto import \
    RecipientUpdateDTO
from txmatching.data_transfer_objects.patients.upload_dto.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dto.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dto.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.db import db
from txmatching.database.services.txm_event_service import \
    remove_donors_and_recipients_from_txm_event
from txmatching.database.sql_alchemy_schema import (
    ConfigModel, DonorModel, RecipientAcceptableBloodModel,
    RecipientHLAAntibodyModel, RecipientModel, TxmEventModel)
from txmatching.patients.patient import (Donor, DonorType, Patient, Recipient,
                                         RecipientRequirements, TxmEvent,
                                         calculate_cutoff)
from txmatching.patients.patient_parameters import (HLAAntibodies, HLAAntibody,
                                                    HLAType, HLATyping,
                                                    PatientParameters)
from txmatching.utils.enums import Country
from txmatching.utils.hla_system.hla_transformations_store import parse_hla_raw_code_and_store_parsing_error_in_db

logger = logging.getLogger(__name__)


def donor_excel_dto_to_donor_model(donor: DonorExcelDTO,
                                   recipient: Optional[RecipientModel],
                                   txm_event_db_id: int) -> DonorModel:
    maybe_recipient_id = recipient.id if recipient else None
    donor_type = DonorType.DONOR if recipient else DonorType.NON_DIRECTED
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


def recipient_excel_dto_to_recipient_model(
        recipient_excel_dto: RecipientExcelDTO,
        txm_event_db_id: int
) -> RecipientModel:
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
        raise ValueError(f'Txm event "{txm_event}" is not empty, cannot send patients to database.')

    maybe_recipient_models = [recipient_excel_dto_to_recipient_model(recipient, txm_event_db_id)
                              if recipient else None for recipient in donors_recipients[1]]
    recipient_models = [recipient_model for recipient_model in maybe_recipient_models if recipient_model]
    db.session.add_all(recipient_models)
    db.session.flush()

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


def update_recipient(recipient_update_dto: RecipientUpdateDTO, txm_event_db_id: int) -> Recipient:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    old_recipient_model = RecipientModel.query.get(recipient_update_dto.db_id)
    if txm_event_db_id != old_recipient_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to.')
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
            RecipientHLAAntibodyModel(
                recipient_id=recipient_update_dto.db_id,
                raw_code=hla_antibody_dto.raw_code,
                mfi=hla_antibody_dto.mfi,
                cutoff=cutoff,
                code=parse_hla_raw_code_and_store_parsing_error_in_db(txm_event_db_id, hla_antibody_dto.raw_code)
            ) for hla_antibody_dto in recipient_update_dto.hla_antibodies_preprocessed.hla_antibodies_list]

        RecipientHLAAntibodyModel.query.filter(
            RecipientHLAAntibodyModel.recipient_id == recipient_update_dto.db_id).delete()
        db.session.add_all(hla_antibodies)
    if recipient_update_dto.hla_typing:
        recipient_update_dict['hla_typing'] = dataclasses.asdict(recipient_update_dto.hla_typing_preprocessed)
    if recipient_update_dto.recipient_requirements:
        recipient_update_dict['recipient_requirements'] = dataclasses.asdict(
            recipient_update_dto.recipient_requirements)
    if recipient_update_dto.cutoff:
        recipient_update_dict['recipient_cutoff'] = recipient_update_dto.cutoff

    RecipientModel.query.filter(RecipientModel.id == recipient_update_dto.db_id).update(recipient_update_dict)
    db.session.commit()
    return _get_recipient_from_recipient_model(RecipientModel.query.get(recipient_update_dto.db_id))


def update_donor(donor_update_dto: DonorUpdateDTO, txm_event_db_id: int) -> Donor:
    # TODO do not delete https://trello.com/c/zseK1Zcf
    old_donor_model = DonorModel.query.get(donor_update_dto.db_id)
    if txm_event_db_id != old_donor_model.txm_event_id:
        raise InvalidArgumentException('Trying to update patient the user has no access to')
    ConfigModel.query.filter(
        and_(ConfigModel.id > 0, ConfigModel.txm_event_id == txm_event_db_id)).delete()

    donor_update_dict = {}
    if donor_update_dto.hla_typing:
        donor_update_dict['hla_typing'] = dataclasses.asdict(donor_update_dto.hla_typing_preprocessed)
    DonorModel.query.filter(DonorModel.id == donor_update_dto.db_id).update(donor_update_dict)
    db.session.commit()
    return _get_donor_from_donor_model(DonorModel.query.get(donor_update_dto.db_id))


def get_txm_event(txm_event_db_id: int) -> TxmEvent:
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


def _parse_date_to_datetime(date: Optional[str]) -> Optional[datetime.datetime]:
    if date is None:
        return None
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    except (ValueError, TypeError) as ex:
        raise InvalidArgumentException(f'Invalid date "{date}". It must be in format "YYYY-MM-DD", e.g.,'
                                       ' "2020-12-31".') from ex


def _recipient_upload_dto_to_recipient_model(
        recipient: RecipientUploadDTO,
        country_code: Country,
        txm_event_db_id: int
) -> RecipientModel:
    hla_antibodies = [RecipientHLAAntibodyModel(
        raw_code=hla_antibody.name,
        code=parse_hla_raw_code_and_store_parsing_error_in_db(txm_event_db_id, hla_antibody.name),
        cutoff=hla_antibody.cutoff,
        mfi=hla_antibody.mfi
    ) for hla_antibody in recipient.hla_antibodies_preprocessed]

    transformed_hla_antibodies = [HLAAntibody(
        raw_code=hla_antibody.raw_code,
        mfi=hla_antibody.mfi,
        code=hla_antibody.code,
        cutoff=hla_antibody.cutoff) for hla_antibody in hla_antibodies]

    acceptable_blood_groups = [] if recipient.acceptable_blood_groups is None \
        else recipient.acceptable_blood_groups

    recipient_model = RecipientModel(
        medical_id=recipient.medical_id,
        country=country_code,
        blood=recipient.blood_group,
        hla_typing=dataclasses.asdict(HLATypingDTO([HLAType(typing) for typing in recipient.hla_typing_preprocessed])),
        hla_antibodies=hla_antibodies,
        active=True,
        acceptable_blood=[RecipientAcceptableBloodModel(blood_type=blood)
                          for blood in acceptable_blood_groups],
        txm_event_id=txm_event_db_id,
        recipient_cutoff=calculate_cutoff(transformed_hla_antibodies),
        waiting_since=_parse_date_to_datetime(recipient.waiting_since),
        weight=recipient.weight,
        height=recipient.height,
        sex=recipient.sex,
        yob=recipient.year_of_birth,
    )
    return recipient_model


def _donor_upload_dto_to_donor_model(
        donor: DonorUploadDTO,
        related_recipient: Optional[RecipientModel],
        country_code: Country,
        txm_event_db_id: int
) -> DonorModel:
    if related_recipient:
        if donor.donor_type != DonorType.DONOR:
            raise InvalidArgumentException(f'When recipient is set, donor type must be "{DonorType.DONOR}".')
    else:
        if donor.donor_type != DonorType.BRIDGING_DONOR and donor.donor_type != DonorType.NON_DIRECTED:
            raise InvalidArgumentException(
                f'When recipient is not set, donor type must be "{DonorType.BRIDGING_DONOR}" '
                f'or "{DonorType.NON_DIRECTED}".')

    maybe_recipient_medical_id = related_recipient.medical_id if related_recipient else None

    assert (donor.related_recipient_medical_id
            and maybe_recipient_medical_id == donor.related_recipient_medical_id
            ) \
           or (not donor.related_recipient_medical_id and not maybe_recipient_medical_id), \
        f'Donor requires recipient medical id "{donor.related_recipient_medical_id}", ' \
        f'but received "{maybe_recipient_medical_id}" or related recipient must be None.'

    donor_model = DonorModel(
        medical_id=donor.medical_id,
        country=country_code,
        blood=donor.blood_group,
        hla_typing=dataclasses.asdict(HLATypingDTO([HLAType(typing) for typing in donor.hla_typing_preprocessed])),
        active=True,
        recipient=related_recipient,
        donor_type=donor.donor_type,
        weight=donor.weight,
        height=donor.height,
        sex=donor.sex,
        yob=donor.year_of_birth,
        txm_event_id=txm_event_db_id
    )
    return donor_model


def _save_patients_to_existing_txm_event(
        donors: List[DonorUploadDTO],
        recipients: List[RecipientUploadDTO],
        country_code: Country,
        txm_event_name: str
):
    related_recipient_medical_ids = [
        donor.related_recipient_medical_id
        for donor in list(filter(lambda donor: donor.related_recipient_medical_id is not None, donors))
    ]

    duplicate_ids = [item for item, count in collections.Counter(related_recipient_medical_ids).items() if count > 1]
    if len(duplicate_ids) > 0:
        raise InvalidArgumentException(f'Duplicate recipient medical ids found: {duplicate_ids}.')

    txm_event = TxmEventModel.query.filter(TxmEventModel.name == txm_event_name).first()
    if not txm_event:
        raise InvalidArgumentException(f'No TXM event with name "{txm_event_name}" found.')

    if len(txm_event.donors) > 0 or len(txm_event.recipients) > 0:
        raise InvalidArgumentException(f'Txm event "{txm_event_name}" is not empty, cannot send patients to database.')

    txm_event_db_id = txm_event.id
    recipient_models = [
        _recipient_upload_dto_to_recipient_model(recipient, country_code, txm_event_db_id)
        for recipient in recipients
    ]
    db.session.add_all(recipient_models)

    recipient_models_dict = {recipient_model.medical_id: recipient_model for recipient_model in recipient_models}

    donor_models = [
        _donor_upload_dto_to_donor_model(
            donor=donor,
            related_recipient=recipient_models_dict.get(donor.related_recipient_medical_id, None),
            country_code=country_code,
            txm_event_db_id=txm_event_db_id)
        for donor in donors
    ]
    db.session.add_all(donor_models)


def update_txm_event_patients(patient_upload_dto: PatientUploadDTOIn, country_code: Country):
    """
    Updates TXM event patients, i.e., removes current event donors and recipients and add new entities.
    :param patient_upload_dto:
    :param country_code:
    :return:
    """
    remove_donors_and_recipients_from_txm_event(patient_upload_dto.txm_event_name)
    _save_patients_to_existing_txm_event(
        donors=patient_upload_dto.donors,
        recipients=patient_upload_dto.recipients,
        country_code=country_code,
        txm_event_name=patient_upload_dto.txm_event_name
    )
    db.session.commit()
