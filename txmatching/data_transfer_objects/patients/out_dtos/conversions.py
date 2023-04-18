from typing import Dict, List, Optional, Union

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.data_transfer_objects.hla.parsing_issue_dto import ParsingIssue
from txmatching.data_transfer_objects.patients.out_dtos.donor_dto_out import \
    DonorDTOOut
from txmatching.data_transfer_objects.patients.out_dtos.recipient_dto_out import \
    RecipientDTOOut
from txmatching.database.services.config_service import \
    find_config_for_parameters
from txmatching.database.services.pairing_result_service import \
    get_pairing_result_comparable_to_config
from txmatching.database.services.parsing_issue_service import \
    get_parsing_issues_for_patients
from txmatching.database.services.scorer_service import \
    compatibility_graph_from_dict
from txmatching.database.services.txm_event_service import get_txm_event_base
from txmatching.patients.patient import Donor, Recipient, TxmEvent
from txmatching.patients.recipient_compatibility import \
    calculate_cpra_and_get_compatible_donors_for_recipient
from txmatching.scorers.additive_scorer import AdditiveScorer
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.enums import StrictnessType
from txmatching.utils.hla_system.compatibility_index import (
    get_detailed_compatibility_index,
    get_detailed_compatibility_index_without_recipient)
from txmatching.utils.hla_system.detailed_score import (
    DetailedScoreForHLAGroup, get_detailed_score)
from txmatching.utils.hla_system.hla_crossmatch import \
    get_crossmatched_antibodies_per_group
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import (
    ERROR_PROCESSING_RESULTS, WARNING_PROCESSING_RESULTS)
from txmatching.utils.recipient_donor_compatibility import \
    RecipientDonorCompatibilityDetails


def to_lists_for_fe(txm_event: TxmEvent, configuration_parameters: ConfigParameters,
                    compute_cpra: bool = False, without_recipient_compatibility: bool = False) \
    -> Dict[str, Union[List[DonorDTOOut], List[RecipientDTOOut]]]:

    scorer = scorer_from_configuration(configuration_parameters)

    if not without_recipient_compatibility:
        # Try to load configuration corresponding to parameters
        configuration = find_config_for_parameters(configuration_parameters, txm_event.db_id)

        # If configuration loaded, try to load compatibility_graph to optimize
        # `calculate_cpra_and_get_compatible_donors_for_recipient`.
        compatibility_graph_of_db_ids = None
        if configuration:
            pairing_result_model = get_pairing_result_comparable_to_config(configuration, txm_event)
            if pairing_result_model is not None:
                compatibility_graph = compatibility_graph_from_dict(pairing_result_model.compatibility_graph)
                compatibility_graph_of_db_ids = scorer.get_compatibility_graph_of_db_ids(
                    txm_event.active_and_valid_recipients_dict, txm_event.active_and_valid_donors_dict, compatibility_graph)

    recipient_dtos = []
    for recipient in txm_event.all_recipients:

        # If not specifically asked not to do so and the compatibility_graph for the `configuration_parameters` is
        # already in db (corresponding pairing result is already computed): for each recipient, find all compatible
        # donors with compatibility details and optionally also compute recipient's cpra value.
        if (not without_recipient_compatibility) and compatibility_graph_of_db_ids:
            recipient_donors_compatibility = \
                calculate_cpra_and_get_compatible_donors_for_recipient(
                    txm_event, recipient, configuration_parameters, compatibility_graph_of_db_ids,
                    compute_compatibility_details=True, compute_cpra=compute_cpra)
            recipient_dto = recipient_to_recipient_dto_out(
                recipient=recipient,
                txm_event_id=txm_event.db_id,
                cpra=recipient_donors_compatibility.cpra,
                compatible_donors_details=recipient_donors_compatibility.compatible_donors_details)
        else:
            recipient_dto = recipient_to_recipient_dto_out(
                recipient=recipient,
                txm_event_id=txm_event.db_id)

        recipient_dtos.append(recipient_dto)

    return {
        'donors': sorted([
            donor_to_donor_dto_out(
                donor, txm_event.all_recipients, configuration_parameters, scorer, txm_event
            ) for donor in txm_event.all_donors],
            key=lambda donor: (
                not donor.active_and_valid_pair, _patient_order_for_fe(donor))),
        'recipients': sorted(recipient_dtos, key=_patient_order_for_fe)
    }


def _patient_order_for_fe(patient: Union[DonorDTOOut, RecipientDTOOut]) -> str:
    return f'{patient.parameters.country_code.value}_{patient.medical_id}'


def recipient_to_recipient_dto_out(
        recipient: Recipient,
        txm_event_id: int,
        cpra: Optional[float] = None,
        compatible_donors_details: Optional[List[RecipientDonorCompatibilityDetails]] = None) -> RecipientDTOOut:
    return RecipientDTOOut(
        db_id=recipient.db_id,
        medical_id=recipient.medical_id,
        parameters=recipient.parameters,
        etag=recipient.etag,
        acceptable_blood_groups=recipient.acceptable_blood_groups,
        hla_antibodies=recipient.hla_antibodies,
        related_donors_db_ids=recipient.related_donors_db_ids,
        parsing_issues=recipient.parsing_issues,
        recipient_cutoff=recipient.recipient_cutoff,
        recipient_requirements=recipient.recipient_requirements,
        waiting_since=recipient.waiting_since,
        previous_transplants=recipient.previous_transplants,
        internal_medical_id=recipient.internal_medical_id,
        all_messages=get_messages(recipient_id=recipient.db_id, txm_event_id=txm_event_id),
        cpra = cpra,
        compatible_donors_details=compatible_donors_details
    )


def donor_to_donor_dto_out(donor: Donor,
                           all_recipients: List[Recipient],
                           config_parameters: ConfigParameters,
                           scorer: AdditiveScorer,
                           txm_event: TxmEvent) -> DonorDTOOut:
    donor_dto = DonorDTOOut(db_id=donor.db_id,
                            medical_id=donor.medical_id,
                            parameters=donor.parameters,
                            etag=donor.etag,
                            donor_type=donor.donor_type,
                            related_recipient_db_id=donor.related_recipient_db_id,
                            active=donor.active,
                            internal_medical_id=donor.internal_medical_id,
                            parsing_issues=donor.parsing_issues,
                            all_messages=get_messages(donor_id=donor.db_id, txm_event_id=txm_event.db_id),
                            active_and_valid_pair=donor.db_id in txm_event.active_and_valid_donors_dict
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
        antibodies = get_crossmatched_antibodies_per_group(
            donor.parameters.hla_typing,
            related_recipient.hla_antibodies,
            config_parameters.use_high_resolution
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

        donor_dto.compatible_blood_with_related_recipient = True
        donor_dto.detailed_score_with_related_recipient = [
            DetailedScoreForHLAGroup(
                recipient_matches=[],
                hla_group=compatibility_index_detailed_group.hla_group,
                group_compatibility_index=compatibility_index_detailed_group.group_compatibility_index,
                antibody_matches=[],
                donor_matches=compatibility_index_detailed_group.donor_matches
            ) for compatibility_index_detailed_group in compatibility_index_detailed if
            len(compatibility_index_detailed_group.donor_matches) != 0
        ]

    return donor_dto


def get_messages(txm_event_id: int, recipient_id: int = None, donor_id: int = None) -> Dict[
    str, List[ParsingIssue]]:
    if donor_id is not None:
        donor_id = [donor_id]
    if recipient_id is not None:
        recipient_id = [recipient_id]

    parsing_issues = get_parsing_issues_for_patients(txm_event_id, donor_id, recipient_id)

    if get_txm_event_base(txm_event_id).strictness_type == StrictnessType.FORGIVING:
        return {
            'infos': list(parsing_issues),
            'warnings': [],
            'errors': []
        }

    return {
        'infos': [],
        'warnings': [
            warning for warning in parsing_issues
            if warning.parsing_issue_detail in WARNING_PROCESSING_RESULTS
        ],
        'errors': [
            error for error in parsing_issues
            if error.parsing_issue_detail in ERROR_PROCESSING_RESULTS]
    }
