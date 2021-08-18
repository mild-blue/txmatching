from typing import Dict, List, Union

from txmatching.configuration.configuration import Configuration
from txmatching.data_transfer_objects.patients.out_dtos.donor_dto_out import \
    DonorDTOOut
from txmatching.data_transfer_objects.patients.out_dtos.recipient_dto_out import \
    RecipientDTOOut
from txmatching.patients.patient import Donor, Recipient, TxmEvent
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, get_detailed_compatibility_index,
    get_detailed_compatibility_index_without_recipient)
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_crossmatched_antibodies)


def to_lists_for_fe(txm_event: TxmEvent, configuration_parameters: Configuration) \
        -> Dict[str, Union[List[DonorDTOOut], List[Recipient]]]:
    scorer = scorer_from_configuration(configuration_parameters)
    return {
        'donors': sorted([donor_to_donor_dto_out(donor, txm_event.all_recipients, configuration_parameters, scorer) for donor in
                          txm_event.all_donors], key=_patient_order_for_fe),
        'recipients': sorted(txm_event.all_recipients, key=_patient_order_for_fe)
    }


def _patient_order_for_fe(patient: Union[DonorDTOOut, Recipient]) -> str:
    return f'{patient.parameters.country_code.value}_{patient.medical_id}'


def recipient_to_recipient_dto_out(recipient: Recipient) -> RecipientDTOOut:
    return recipient


def donor_to_donor_dto_out(donor: Donor,
                           all_recipients: List[Recipient],
                           configuration: Configuration,
                           scorer: AdditiveScorer) -> DonorDTOOut:
    donor_dto = DonorDTOOut(db_id=donor.db_id,
                            medical_id=donor.medical_id,
                            parameters=donor.parameters,
                            donor_type=donor.donor_type,
                            related_recipient_db_id=donor.related_recipient_db_id,
                            active=donor.active,
                            internal_medical_id=donor.internal_medical_id
                            )
    if donor.related_recipient_db_id:
        related_recipient = next(recipient for recipient in all_recipients if
                                 recipient.db_id == donor.related_recipient_db_id)

        donor_dto.score_with_related_recipient = scorer.score_transplant(donor, related_recipient, None)
        donor_dto.max_score_with_related_recipient = scorer.max_transplant_score
        donor_dto.compatible_blood_with_related_recipient = blood_groups_compatible(
            donor.parameters.blood_group,
            related_recipient.parameters.blood_group
        )
        antibodies = get_crossmatched_antibodies(
            donor.parameters.hla_typing,
            related_recipient.hla_antibodies,
            configuration.use_high_resolution
        )
        compatibility_index_detailed = get_detailed_compatibility_index(
            donor_hla_typing=donor.parameters.hla_typing,
            recipient_hla_typing=related_recipient.parameters.hla_typing,
            ci_configuration=scorer.ci_configuration)
        donor_dto.detailed_score_with_related_recipient = get_detailed_score(
            compatibility_index_detailed,
            antibodies
        )
    else:
        compatibility_index_detailed = get_detailed_compatibility_index_without_recipient(
            donor_hla_typing=donor.parameters.hla_typing
        )

        donor_dto.detailed_score_with_related_recipient = [
            DetailedScoreForHLAGroup(
                recipient_matches=[],
                hla_group=compatibility_index_detailed_group.hla_group,
                group_compatibility_index=compatibility_index_detailed_group.group_compatibility_index,
                antibody_matches=[],
                donor_matches=compatibility_index_detailed_group.donor_matches
            ) for compatibility_index_detailed_group in compatibility_index_detailed
        ]

    return donor_dto


def get_detailed_score(compatibility_index_detailed: List[DetailedCompatibilityIndexForHLAGroup],
                       antibodies: List[AntibodyMatchForHLAGroup]) -> List[DetailedScoreForHLAGroup]:
    assert len(antibodies) == len(compatibility_index_detailed)
    detailed_scores = []
    for antibody_group, compatibility_index_detailed_group in zip(antibodies, compatibility_index_detailed):
        assert antibody_group.hla_group == compatibility_index_detailed_group.hla_group
        detailed_scores.append(
            DetailedScoreForHLAGroup(
                recipient_matches=compatibility_index_detailed_group.recipient_matches,
                hla_group=compatibility_index_detailed_group.hla_group,
                group_compatibility_index=compatibility_index_detailed_group.group_compatibility_index,
                antibody_matches=antibody_group.antibody_matches,
                donor_matches=compatibility_index_detailed_group.donor_matches
            )
        )
    return detailed_scores
