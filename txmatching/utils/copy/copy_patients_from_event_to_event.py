from typing import List

from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.database.services.txm_event_service import \
    get_txm_event_complete
from txmatching.utils.export.export_txm_event import \
    get_patients_upload_json_from_txm_event_for_country


def copy_patients_between_events(txm_event_id_from: int, txm_event_id_to: int, donor_ids: List[int]) -> List[int]:
    txm_event_from = get_txm_event_complete(txm_event_id_from, load_antibodies_raw=True)
    txm_event_to = get_txm_event_complete(txm_event_id_to, load_antibodies_raw=True)
    donors_to_copy = [donor for donor in txm_event_from.active_and_valid_donors_dict.values()
                      if donor.db_id in donor_ids]

    donor_related_recipients = [
        txm_event_from.active_and_valid_recipients_dict[donor.related_recipient_db_id] for donor in donors_to_copy if
        donor.related_recipient_db_id is not None]

    # raise error if the recipient is already in the event
    txm_event_to_recipient_medical_ids = [recipient.medical_id for recipient in
                                          txm_event_to.active_and_valid_recipients_dict.values()]

    for recipient in donor_related_recipients:
        if recipient.medical_id in txm_event_to_recipient_medical_ids:
            raise ValueError(
                f'Recipient with medical id {recipient.medical_id} already exists in event {txm_event_to.name}. '
                f'Unfortunately, we do not support copying donors with the related recipient that is'
                f' already in TxmEventTo yet.')

    # actual copying
    donor_countries = set(donor.parameters.country_code for donor in donors_to_copy)
    donor_ids_to_copy_by_country = {country: [donor.medical_id for donor in donors_to_copy
                                              if donor.parameters.country_code == country] for country in
                                    donor_countries}

    patient_upload_dtos_for_country = [
        get_patients_upload_json_from_txm_event_for_country(txm_event_id_from,
                                                            country,
                                                            txm_event_to.name,
                                                            donor_ids)
        for country, donor_ids in donor_ids_to_copy_by_country.items()]

    new_donor_ids = []
    for patient_upload_dto in patient_upload_dtos_for_country:
        patients = replace_or_add_patients_from_one_country(patient_upload_dto=patient_upload_dto)
        new_donor_ids = new_donor_ids + [donor.id for donor in patients[0]]

    return new_donor_ids
