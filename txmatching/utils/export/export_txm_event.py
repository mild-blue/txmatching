from typing import List, Optional

from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.patients.patient import Donor, TxmEvent
from txmatching.utils.country_enum import Country


def get_id_or_none(donor: Optional[Donor], txm_event: TxmEvent) -> Optional[str]:
    if donor.related_recipient_db_id is not None:
        return txm_event.active_and_valid_recipients_dict[donor.related_recipient_db_id].medical_id
    else:
        return None


def get_patients_upload_json_from_txm_event_for_country(
        txm_event_id: int,
        country_code: Country,
        txm_event_name: str,
) -> PatientUploadDTOIn:
    txm_event = get_txm_event_complete(txm_event_id, load_antibodies_raw=True)
    donors = [
        DonorUploadDTO(
            medical_id=donor.medical_id,
            blood_group=donor.parameters.blood_group,
            hla_typing=[code.raw_code for code in donor.parameters.hla_typing.hla_types_raw_list],
            donor_type=donor.donor_type,
            related_recipient_medical_id=get_id_or_none(donor, txm_event),
            sex=donor.parameters.sex,
            height=donor.parameters.height,
            weight=donor.parameters.weight,
            year_of_birth=donor.parameters.year_of_birth,
            note=donor.parameters.note,
            internal_medical_id=None
        )
        for donor in
        txm_event.active_and_valid_donors_dict.values() if donor.parameters.country_code == country_code
    ]
    recipients = [
        RecipientUploadDTO(
            medical_id=recipient.medical_id,
            blood_group=recipient.parameters.blood_group,
            hla_typing=[code.raw_code for code in recipient.parameters.hla_typing.hla_types_raw_list],
            sex=recipient.parameters.sex,
            height=recipient.parameters.height,
            weight=recipient.parameters.weight,
            year_of_birth=recipient.parameters.year_of_birth,
            note=recipient.parameters.note,
            internal_medical_id=None,
            hla_antibodies=[HLAAntibodiesUploadDTO(
                cutoff=code.cutoff,
                mfi=code.mfi,
                name=code.raw_code
            ) for code in recipient.hla_antibodies.hla_antibodies_raw_list],
            waiting_since=recipient.waiting_since.strftime('%Y-%m-%d') if recipient.waiting_since is not None else None,
            previous_transplants=recipient.previous_transplants,
            acceptable_blood_groups=recipient.acceptable_blood_groups
        )
        for recipient in
        txm_event.active_and_valid_recipients_dict.values() if recipient.parameters.country_code == country_code
    ]

    return PatientUploadDTOIn(
        country=country_code,
        txm_event_name=txm_event_name,
        donors=donors,
        recipients=recipients,
        add_to_existing_patients=False
    )


def get_patients_upload_json_from_txm_event_for_country_and_donor_ids(
        txm_event_id: int,
        country_code: Country,
        txm_event_name: str,
        donor_medical_ids: List[str]
) -> PatientUploadDTOIn:
    txm_event = get_txm_event_complete(txm_event_id, load_antibodies_raw=True)
    donors = [
        DonorUploadDTO(
            medical_id=donor.medical_id,
            blood_group=donor.parameters.blood_group,
            hla_typing=[code.raw_code for code in donor.parameters.hla_typing.hla_types_raw_list],
            donor_type=donor.donor_type,
            related_recipient_medical_id=get_id_or_none(donor, txm_event),
            sex=donor.parameters.sex,
            height=donor.parameters.height,
            weight=donor.parameters.weight,
            year_of_birth=donor.parameters.year_of_birth,
            note=donor.parameters.note,
            internal_medical_id=None
        )
        for donor in
        txm_event.active_and_valid_donors_dict.values()
        if donor.parameters.country_code == country_code and donor.medical_id in donor_medical_ids
    ]
    related_recipient_medical_ids = [donor.related_recipient_medical_id for donor in donors]

    recipients = [
        RecipientUploadDTO(
            medical_id=recipient.medical_id,
            blood_group=recipient.parameters.blood_group,
            hla_typing=[code.raw_code for code in recipient.parameters.hla_typing.hla_types_raw_list],
            sex=recipient.parameters.sex,
            height=recipient.parameters.height,
            weight=recipient.parameters.weight,
            year_of_birth=recipient.parameters.year_of_birth,
            note=recipient.parameters.note,
            internal_medical_id=None,
            hla_antibodies=[HLAAntibodiesUploadDTO(
                cutoff=code.cutoff,
                mfi=code.mfi,
                name=code.raw_code
            ) for code in recipient.hla_antibodies.hla_antibodies_raw_list],
            waiting_since=recipient.waiting_since.strftime('%Y-%m-%d') if recipient.waiting_since is not None else None,
            previous_transplants=recipient.previous_transplants,
            acceptable_blood_groups=recipient.acceptable_blood_groups
        )
        for recipient in
        txm_event.active_and_valid_recipients_dict.values() 
        if recipient.parameters.country_code == country_code and recipient.medical_id in related_recipient_medical_ids
    ]

    return PatientUploadDTOIn(
        country=country_code,
        txm_event_name=txm_event_name,
        donors=donors,
        recipients=recipients,
        add_to_existing_patients=True
    )
