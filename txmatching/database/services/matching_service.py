import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from txmatching.data_transfer_objects.matchings.matching_dto import (
    CalculatedMatchingsDTO, MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.data_transfer_objects.patients.out_dtos.conversions import \
    get_detailed_score
from txmatching.database.services.config_service import (
    get_configuration_from_db_id_or_default,
    get_pairing_result_for_configuration_db_id)
from txmatching.patients.patient import Donor, Recipient, TxmEvent
from txmatching.scorers.matching import get_count_of_transplants
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.enums import AntibodyMatchTypes
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, get_detailed_compatibility_index)
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_crossmatched_antibodies)

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


def get_matchings_detailed_for_configuration(txm_event: TxmEvent,
                                             configuration_db_id: int) -> MatchingsDetailed:
    logger.debug('Getting detailed matchings')
    configuration = get_configuration_from_db_id_or_default(txm_event, configuration_db_id)
    scorer = scorer_from_configuration(configuration)

    database_pairing_result = get_pairing_result_for_configuration_db_id(configuration_db_id)
    logger.debug('Getting matchings with score')
    matchings_with_score = _matchings_dto_to_matching_with_score(database_pairing_result.matchings,
                                                                 txm_event.active_donors_dict,
                                                                 txm_event.active_recipients_dict)
    logger.debug('Getting score dict with score')
    score_dict = {
        (donor_db_id, recipient_db_id): score for donor_db_id, row in
        zip(txm_event.active_donors_dict, database_pairing_result.score_matrix) for recipient_db_id, score in
        zip(txm_event.active_recipients_dict, row)
    }
    logger.debug('Getting compatible_blood dict with score')
    compatible_blood_dict = {(donor_db_id, recipient_db_id): blood_groups_compatible(donor.parameters.blood_group,
                                                                                     recipient.parameters.blood_group)
                             for donor_db_id, donor in txm_event.active_donors_dict.items()
                             for recipient_db_id, recipient in txm_event.active_recipients_dict.items() if
                             score_dict[(donor_db_id, recipient_db_id)] >= 0
                             }
    logger.debug('Getting has crossmatch')
    logger.debug('Getting ci dict dict with score')
    detailed_compatibility_index_dict = {
        (donor_db_id, recipient_db_id): get_detailed_compatibility_index(donor.parameters.hla_typing,
                                                                         recipient.parameters.hla_typing,
                                                                         ci_configuration=scorer.ci_configuration)
        for donor_db_id, donor in txm_event.active_donors_dict.items()
        for recipient_db_id, recipient in txm_event.active_recipients_dict.items() if
        score_dict[(donor_db_id, recipient_db_id)] >= 0
    }
    logger.debug('Getting antibody matches dict dict with score')
    antibody_matches_dict = {
        (donor_db_id, recipient_db_id): get_crossmatched_antibodies(donor.parameters.hla_typing,
                                                                    recipient.hla_antibodies,
                                                                    configuration.use_high_resolution
                                                                    )
        for donor_db_id, donor in txm_event.active_donors_dict.items()
        for recipient_db_id, recipient in txm_event.active_recipients_dict.items() if
        score_dict[(donor_db_id, recipient_db_id)] >= 0
    }

    return MatchingsDetailed(
        matchings_with_score,
        score_dict,
        compatible_blood_dict,
        detailed_compatibility_index_dict,
        antibody_matches_dict,
        database_pairing_result.matchings.found_matchings_count,
        database_pairing_result.matchings.show_not_all_matchings_found,
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
                list(DonorRecipientPair(donors_dict[donor_recipient_ids.donor],
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
        has_crossmatch = len([antibody_match for detailed_score in detailed_scores
                              for antibody_match in detailed_score.antibody_matches
                              if antibody_match.match_type != AntibodyMatchTypes.NONE]) > 0

        return TransplantDTOOut(
            score=latest_matchings_detailed.scores_tuples[(pair.donor.db_id, pair.recipient.db_id)],
            max_score=latest_matchings_detailed.max_transplant_score,
            compatible_blood=latest_matchings_detailed.blood_compatibility_tuples[
                (pair.donor.db_id, pair.recipient.db_id)],
            has_crossmatch=has_crossmatch,
            donor=pair.donor.medical_id,
            recipient=pair.recipient.medical_id,
            detailed_score_per_group=detailed_scores
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
