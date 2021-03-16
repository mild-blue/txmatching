import random
import re
from typing import List, Optional, Tuple

import pandas as pd

from tests.test_utilities.populate_db import create_or_overwrite_txm_event
from txmatching.data_transfer_objects.patients.upload_dtos.donor_upload_dto import \
    DonorUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.hla_antibodies_upload_dto import \
    HLAAntibodiesUploadDTO
from txmatching.data_transfer_objects.patients.upload_dtos.patient_upload_dto_in import \
    PatientUploadDTOIn
from txmatching.data_transfer_objects.patients.upload_dtos.recipient_upload_dto import \
    RecipientUploadDTO
from txmatching.database.services.patient_upload_service import \
    replace_or_add_patients_from_one_country
from txmatching.patients.patient import DonorType
from txmatching.utils.blood_groups import BloodGroup
from txmatching.utils.country_enum import Country
from txmatching.utils.enums import HLA_GROUP_SPLIT_CODE_REGEX, HLAGroup, Sex
from txmatching.utils.hla_system.rel_dna_ser_parsing import \
    HIGH_RES_TO_SPLIT_OR_BROAD
from txmatching.web import create_app

BRIDGING_PROBABILITY = 0.8


def random_true_with_prob(prob: float):
    return random.uniform(0, 1) > prob


def random_blood_group() -> BloodGroup:
    rand = random.uniform(0, 1)
    if rand < 0.15:
        return BloodGroup.ZERO
    if rand < 0.5:
        return BloodGroup.A
    if rand < 0.9:
        return BloodGroup.B
    else:
        return BloodGroup.AB


SAMPLE = set(range(1, 40))


def get_codes(hla_group: HLAGroup, sample=None):
    if sample is None:
        sample = SAMPLE
    all_high_res = [high_res for high_res, split_or_broad_or_nan in HIGH_RES_TO_SPLIT_OR_BROAD.items() if
                    split_or_broad_or_nan is not None and not pd.isna(split_or_broad_or_nan) and re.match(
                        HLA_GROUP_SPLIT_CODE_REGEX[hla_group], split_or_broad_or_nan) and high_res.count(':') == 1]
    return [high_res for i, high_res in enumerate(all_high_res) if i in sample]


TypizationFor = {
    HLAGroup.A: get_codes(HLAGroup.A),
    HLAGroup.B: get_codes(HLAGroup.B),
    HLAGroup.DRB1: get_codes(HLAGroup.DRB1),
    # HLAGroup.CW: get_codes(HLAGroup.CW),
    HLAGroup.DP: get_codes(HLAGroup.DP),
    HLAGroup.DQ: get_codes(HLAGroup.DQ)
}


def get_random_hla_type(hla_group: HLAGroup):
    return random.choice(TypizationFor[hla_group])


def generate_hla_typing() -> List[str]:
    typization = []
    for hla_group in TypizationFor:
        typization.append(get_random_hla_type(hla_group))
        typization.append(get_random_hla_type(hla_group))

    return typization


CUTOFF = 2000


def generate_antibodies() -> List[HLAAntibodiesUploadDTO]:
    antibodies = []
    for hla_group in TypizationFor:
        for hla_code in TypizationFor[hla_group]:
            above_cutoff = random_true_with_prob(0.8)
            mfi = int(CUTOFF * 2) if above_cutoff else int(CUTOFF / 2)
            antibodies.append(HLAAntibodiesUploadDTO(
                cutoff=CUTOFF,
                mfi=mfi,
                name=hla_code
            ))
    return antibodies


def generate_patient(country: Country, i: int) -> Tuple[DonorUploadDTO, Optional[RecipientUploadDTO]]:
    is_bridging = random_true_with_prob(BRIDGING_PROBABILITY)
    blood_group_donor = random_blood_group()
    donor_type = DonorType.BRIDGING_DONOR if is_bridging else DonorType.DONOR
    recipient_id = f'{country}_{i}R' if not is_bridging else None
    donor = DonorUploadDTO(
        donor_type=donor_type,
        blood_group=blood_group_donor,
        related_recipient_medical_id=recipient_id,
        hla_typing=generate_hla_typing(),
        medical_id=f'{country}_{i}',
        height=173,
        weight=90,
        year_of_birth=1985,
        sex=Sex.F,
    )
    if is_bridging:
        recipient = None
    else:
        blood_group_recipient = random_blood_group()
        recipient = RecipientUploadDTO(
            blood_group=blood_group_recipient,
            hla_typing=generate_hla_typing(),
            hla_antibodies=generate_antibodies(),
            acceptable_blood_groups=[],
            medical_id=recipient_id,
            height=173,
            weight=90,
            year_of_birth=1985,
            sex=Sex.F,
        )

    return donor, recipient


def generate_patients(country: Country, txm_event_name: str, count: int) -> PatientUploadDTOIn:
    pairs = [generate_patient(country, i) for i in range(0, count)]
    recipients = [recipient for _, recipient in pairs if recipient]
    donors = [donor for donor, _ in pairs]

    return PatientUploadDTOIn(
        add_to_existing_patients=False,
        txm_event_name=txm_event_name,
        country=country,
        recipients=recipients,
        donors=donors,
    )


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        txm_event = create_or_overwrite_txm_event(name='random_data')
        replace_or_add_patients_from_one_country(
            generate_patients(Country.CZE, txm_event_name=txm_event.name, count=10))
        replace_or_add_patients_from_one_country(
            generate_patients(Country.IND, txm_event_name=txm_event.name, count=10))
        replace_or_add_patients_from_one_country(
            generate_patients(Country.CAN, txm_event_name=txm_event.name, count=10))
