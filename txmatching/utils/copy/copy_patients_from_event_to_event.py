from txmatching.data_transfer_objects.patients.upload_dtos.donor_recipient_pair_upload_dtos import DonorRecipientPairDTO
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.patient_upload_service import add_donor_recipient_pair
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete

def get_patients_from_event(txm_event_id_from: int, donor_ids: list) -> PatientUploadDTOIn:
    txm_event_from = get_txm_event_complete(txm_event_id_from, load_antibodies_raw=True)  
    donors = []
    related_recipients_ids = []

    for donor_id in donor_ids:
        donor = txm_event_from.active_and_valid_donors_dict[donor_id]
        related_recipients_ids.append(donor.related_recipient_db_id)
        donors.append(DonorUploadDTO(
            medical_id=donor.medical_id,
            blood_group=donor.parameters.blood_group,
            hla_typing=[code.raw_code for code in donor.parameters.hla_typing.hla_types_raw_list],
            donor_type=donor.donor_type,
            related_recipient_medical_id=donor.related_recipient_db_id,
            sex = donor.parameters.sex,
            height= donor.parameters.height,
            weight=donor.parameters.weight,
            year_of_birth=donor.parameters.year_of_birth,
            note = donor.parameters.note,
            internal_medical_id=None
            ))

    recipients = []
    for recipient_id in related_recipients_ids:
        recipient = txm_event_from.active_and_valid_recipients_dict[recipient_id]
        recipients.append(RecipientUploadDTO(
            acceptable_blood_groups=recipient.acceptable_blood_groups,
            medical_id=recipient.medical_id,
            blood_group=recipient.parameters.blood_group,
            hla_typing=[code.raw_code for code in recipient.parameters.hla_typing.hla_types_raw_list],
            hla_antibodies=[HLAAntibodiesUploadDTO(
                cutoff=code.cutoff,
                mfi=code.mfi,
                name=code.raw_code
            ) for code in recipient.hla_antibodies.hla_antibodies_raw_list],
            sex = recipient.parameters.sex,
            height= recipient.parameters.height,
            weight=recipient.parameters.weight,
            year_of_birth=recipient.parameters.year_of_birth,
            note = recipient.parameters.note,
            previous_transplants=recipient.parameters.previous_transplants,
            internal_medical_id=None))

    return PatientUploadDTOIn(
        country=donors[0].country,
        txm_event_name=txm_event_from.name,
        donors=donors,
        recipients=recipients,
        add_to_existing_patients=True
    )


def load_patients_to_event(txm_event_id_to: int, patient_dto: PatientUploadDTOIn) -> list:
    donor_ids = []

    for donor in patient_dto.donors:
        for recipient in patient_dto.recipients:
            if donor.related_recipient_medical_id == recipient.medical_id:
                rel_recipient = recipient
        donor_recipient_pair = DonorRecipientPairDTO(
            country_code=patient_dto.country,
            donor=donor,
            recipient=rel_recipient
        )
        pair = add_donor_recipient_pair(donor_recipient_pair, txm_event_id_to)
        donor_ids.append(pair[0].id)      
    return donor_ids
