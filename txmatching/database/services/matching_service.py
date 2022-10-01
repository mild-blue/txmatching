import logging
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Tuple

from txmatching.data_transfer_objects.matchings.matching_dto import (
    CalculatedMatchingsDTO, MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.data_transfer_objects.patients.out_dtos.conversions import \
    get_detailed_score
from txmatching.database.services.config_service import \
    configuration_from_config_model
from txmatching.database.services.scorer_service import (
    compatibility_graph_from_dict, matchings_model_from_dict)
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.patients.patient import (Donor, Recipient,
                                         RecipientRequirements, TxmEvent)
from txmatching.patients.patient_parameters import PatientParameters
from txmatching.scorers.matching import get_count_of_transplants
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.enums import AntibodyMatchTypes
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, get_detailed_compatibility_index)
from txmatching.utils.hla_system.detailed_score import DetailedScoreForHLAGroup
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_crossmatched_antibodies)
from txmatching.utils.transplantation_warning import (TransplantWarningDetail,
                                                      TransplantWarnings)

logger = logging.getLogger(__name__)


@dataclass
class MatchingsDetailed:
    # pylint: disable=too-many-instance-attributes
    matchings: List[MatchingWithScore]
    scores_tuples: Dict[Tuple[int, int], float]
    blood_compatibility_tuples: Dict[Tuple[int, int], bool]
    detailed_score_tuples: Dict[Tuple[int, int], List[DetailedCompatibilityIndexForHLAGroup]]
    antibody_matches_tuples: Dict[Tuple[int, int], List[AntibodyMatchForHLAGroup]]
    found_matchings_count: Optional[int]
    show_not_all_matchings_found: bool
    max_transplant_score: float


def get_matchings_detailed_for_pairing_result_model(
        pairing_result_model: PairingResultModel,
        txm_event: TxmEvent
) -> MatchingsDetailed:
    logger.debug(f'Getting detailed matchings for pairing result {pairing_result_model.id}')
    configuration_parameters = configuration_from_config_model(pairing_result_model.original_config).parameters
    scorer = scorer_from_configuration(configuration_parameters)

    compatibility_graph = compatibility_graph_from_dict(pairing_result_model.compatibility_graph)
    matchings_model = matchings_model_from_dict(pairing_result_model.calculated_matchings)

    logger.debug('Getting matchings with score')
    matchings_with_score = _matchings_dto_to_matching_with_score(matchings_model,
                                                                 txm_event.active_and_valid_donors_dict,
                                                                 txm_event.active_and_valid_recipients_dict)
    logger.debug('Getting score dict with score')
    compatibility_graph_of_db_ids = scorer.get_compatibility_graph_of_db_ids(txm_event.active_and_valid_recipients_dict,
                                                                             txm_event.active_and_valid_donors_dict,
                                                                             compatibility_graph)
    logger.debug('Getting compatible_blood dict with score')
    compatible_blood_dict = {(pair[0], pair[1]): blood_groups_compatible(
        txm_event.active_and_valid_donors_dict[pair[0]].parameters.blood_group,
        txm_event.active_and_valid_recipients_dict[pair[1]].parameters.blood_group) for pair in
        compatibility_graph_of_db_ids.keys()}
    logger.debug('Getting has crossmatch')
    logger.debug('Getting ci dict dict with score')
    detailed_compatibility_index_dict = {
        (pair[0], pair[1]): get_detailed_compatibility_index(
            txm_event.active_and_valid_donors_dict[pair[0]].parameters.hla_typing,
            txm_event.active_and_valid_recipients_dict[pair[1]].parameters.hla_typing,
            ci_configuration=scorer.ci_configuration) for pair in compatibility_graph_of_db_ids.keys()}
    logger.debug('Getting antibody matches dict dict with score')
    antibody_matches_dict = {
        (pair[0], pair[1]): get_crossmatched_antibodies(
            txm_event.active_and_valid_donors_dict[pair[0]].parameters.hla_typing,
            txm_event.active_and_valid_recipients_dict[pair[1]].hla_antibodies,
            configuration_parameters.use_high_resolution) for pair in compatibility_graph_of_db_ids.keys()}

    return MatchingsDetailed(
        matchings_with_score,
        compatibility_graph_of_db_ids,
        compatible_blood_dict,
        detailed_compatibility_index_dict,
        antibody_matches_dict,
        matchings_model.found_matchings_count,
        matchings_model.show_not_all_matchings_found,
        scorer.max_transplant_score
    )


def _matchings_dto_to_matching_with_score(
        calculated_matchings: MatchingsModel,
        donors_dict: Dict[int, Donor],
        recipients_dict: Dict[int, Recipient],
) -> List[MatchingWithScore]:
    matching_list = []
    for json_matching in calculated_matchings.matchings:
        matching_list.append(
            MatchingWithScore(
                frozenset(DonorRecipientPair(donors_dict[donor_recipient_ids.donor],
                                             recipients_dict[donor_recipient_ids.recipient])
                          for donor_recipient_ids in json_matching.donors_recipients
                          ),
                json_matching.score,
                json_matching.db_id
            )

        )
    return matching_list


def create_calculated_matchings_dto(
        latest_matchings_detailed: MatchingsDetailed,
        matchings: List[MatchingWithScore],
        configuration_db_id: int,
) -> CalculatedMatchingsDTO:
    """
    Method that creates common DTOs for FE and reports.
    """
    logger.debug('Creating calculated matchings DTO')

    def _create_transplant_dto(pair: DonorRecipientPair):
        detailed_scores = get_detailed_score(
            latest_matchings_detailed.detailed_score_tuples[
                (pair.donor.db_id, pair.recipient.db_id)],
            latest_matchings_detailed.antibody_matches_tuples[
                (pair.donor.db_id, pair.recipient.db_id)]
        )

        return TransplantDTOOut(
            score=latest_matchings_detailed.scores_tuples[(pair.donor.db_id, pair.recipient.db_id)],
            max_score=latest_matchings_detailed.max_transplant_score,
            compatible_blood=latest_matchings_detailed.blood_compatibility_tuples[
                (pair.donor.db_id, pair.recipient.db_id)],
            donor=pair.donor.medical_id,
            recipient=pair.recipient.medical_id,
            detailed_score_per_group=detailed_scores,
            transplant_messages=get_transplant_messages(
                pair.donor.parameters,
                pair.recipient.recipient_requirements,
                detailed_scores
            )
        )

    return CalculatedMatchingsDTO(
        calculated_matchings=[MatchingDTO(
            rounds=[
                RoundDTO(
                    transplants=[
                        _create_transplant_dto(pair)
                        for pair in matching_round.donor_recipient_pairs], )
                for matching_round in matching.get_rounds()],
            countries=matching.get_country_codes_counts(),
            score=matching.score,
            order_id=matching.order_id,
            count_of_transplants=get_count_of_transplants(matching)
        ) for matching in matchings
        ],
        found_matchings_count=latest_matchings_detailed.found_matchings_count,
        show_not_all_matchings_found=latest_matchings_detailed.show_not_all_matchings_found,
        config_id=configuration_db_id
    )


def get_transplant_messages(
        donor_parameters: PatientParameters,
        recipient_requirements: RecipientRequirements,
        detailed_scores: List[DetailedScoreForHLAGroup]
) -> TransplantWarnings:
    detailed_messages = []

    if donor_parameters.weight:
        if recipient_requirements.max_donor_weight and donor_parameters.weight > recipient_requirements.max_donor_weight:
            detailed_messages.append(TransplantWarningDetail.MAX_WEIGHT(recipient_requirements.max_donor_weight))
        elif recipient_requirements.min_donor_weight and donor_parameters.weight < recipient_requirements.min_donor_weight:
            detailed_messages.append(TransplantWarningDetail.MIN_WEIGHT(recipient_requirements.min_donor_weight))

    if donor_parameters.height:
        if recipient_requirements.max_donor_height and donor_parameters.height > recipient_requirements.max_donor_height:
            detailed_messages.append(TransplantWarningDetail.MAX_HEIGHT(recipient_requirements.max_donor_height))
        elif recipient_requirements.min_donor_height and donor_parameters.height < recipient_requirements.min_donor_height:
            detailed_messages.append(TransplantWarningDetail.MIN_HEIGHT(recipient_requirements.min_donor_height))

    if donor_parameters.year_of_birth:
        donor_age = date.today().year - donor_parameters.year_of_birth
        if recipient_requirements.max_donor_age and donor_age > recipient_requirements.max_donor_age:
            detailed_messages.append(TransplantWarningDetail.MAX_AGE(recipient_requirements.max_donor_age))
        elif recipient_requirements.min_donor_age and donor_age < recipient_requirements.min_donor_age:
            detailed_messages.append(TransplantWarningDetail.MIN_AGE(recipient_requirements.min_donor_age))

    possible_crossmatches = [antibody_match for detailed_score in detailed_scores
                             for antibody_match in detailed_score.antibody_matches
                             if antibody_match.match_type != AntibodyMatchTypes.NONE]

    broad_crossmatches = {possible_crossmatch.hla_antibody.raw_code for possible_crossmatch in possible_crossmatches
                          if possible_crossmatch.match_type in [AntibodyMatchTypes.BROAD,
                                                                AntibodyMatchTypes.HIGH_RES_WITH_BROAD]}
    split_crossmatches = {possible_crossmatch.hla_antibody.raw_code for possible_crossmatch in possible_crossmatches
                          if possible_crossmatch.match_type in [AntibodyMatchTypes.SPLIT,
                                                                AntibodyMatchTypes.HIGH_RES_WITH_SPLIT]}

    undecidable_crossmatches = {possible_crossmatch.hla_antibody.code.group.name for possible_crossmatch
                                in possible_crossmatches if
                                possible_crossmatch.match_type == AntibodyMatchTypes.UNDECIDABLE and
                                possible_crossmatch.hla_antibody.code}

    if broad_crossmatches != set():
        detailed_messages.append(TransplantWarningDetail.BROAD_CROSSMATCH(broad_crossmatches))

    if split_crossmatches != set():
        detailed_messages.append(TransplantWarningDetail.SPLIT_CROSSMATCH(split_crossmatches))

    if undecidable_crossmatches != set():
        detailed_messages.append(TransplantWarningDetail.UNDECIDABLE(undecidable_crossmatches))

    return TransplantWarnings(
        message_global='There were several issues with this transplant, see detail.',
        all_messages={
            'infos': [],
            'warnings': detailed_messages,
            'errors': []
        }) if detailed_messages else None
