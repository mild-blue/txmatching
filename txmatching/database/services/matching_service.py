from dataclasses import dataclass
from typing import Dict, List, Tuple

from txmatching.data_transfer_objects.matchings.matching_dto import (
    CalculatedMatchingsDTO, MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.matchings.matchings_model import \
    MatchingsModel
from txmatching.data_transfer_objects.patients.out_dots.conversions import \
    get_detailed_score
from txmatching.database.services.config_service import (
    config_set_updated, get_configuration_from_db_id,
    get_latest_config_model_for_txm_event,
    get_pairing_result_for_configuration_db_id)
from txmatching.patients.patient import Donor, Recipient, TxmEvent
from txmatching.scorers.matching import get_count_of_transplants
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, get_detailed_compatibility_index)
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_crossmatched_antibodies)


@dataclass
class MatchingsDetailed:
    matchings: List[MatchingWithScore]
    scores_tuples: Dict[Tuple[int, int], float]
    blood_compatibility_tuples: Dict[Tuple[int, int], bool]
    detailed_score_tuples: Dict[Tuple[int, int], List[DetailedCompatibilityIndexForHLAGroup]]
    antibody_matches_tuples: Dict[Tuple[int, int], List[AntibodyMatchForHLAGroup]]
    found_matchings_count: int
    all_matchings_found: bool


def get_matchings_detailed_for_configuration(txm_event: TxmEvent,
                                             configuration_db_id: int) -> MatchingsDetailed:
    configuration = get_configuration_from_db_id(configuration_db_id)

    config_set_updated(configuration_db_id)
    database_pairing_result = get_pairing_result_for_configuration_db_id(configuration_db_id)

    matchings_with_score = _matchings_dto_to_matching_with_score(database_pairing_result.matchings,
                                                                 txm_event.active_donors_dict,
                                                                 txm_event.active_recipients_dict)
    scorer = scorer_from_configuration(configuration)

    score_dict = {
        (donor.db_id, recipient.db_id): scorer.score_transplant(donor, recipient, txm_event.active_donors_dict[
            recipient.related_donor_db_id]) for donor in
        txm_event.active_donors_dict.values() for recipient in
        txm_event.active_recipients_dict.values()
    }

    compatible_blood_dict = {(donor_db_id, recipient_db_id): blood_groups_compatible(donor.parameters.blood_group,
                                                                                     recipient.parameters.blood_group)
                             for donor_db_id, donor in txm_event.active_donors_dict.items()
                             for recipient_db_id, recipient in txm_event.active_recipients_dict.items()
                             }

    detailed_compatibility_index_dict = {
        (donor_db_id, recipient_db_id): get_detailed_compatibility_index(donor.parameters.hla_typing,
                                                                         recipient.parameters.hla_typing)
        for donor_db_id, donor in txm_event.active_donors_dict.items()
        for recipient_db_id, recipient in txm_event.active_recipients_dict.items()
    }

    antibody_matches_dict = {
        (donor_db_id, recipient_db_id): get_crossmatched_antibodies(donor.parameters.hla_typing,
                                                                    recipient.hla_antibodies,
                                                                    configuration.use_split_resolution
                                                                    )
        for donor_db_id, donor in txm_event.active_donors_dict.items()
        for recipient_db_id, recipient in txm_event.active_recipients_dict.items()
    }

    return MatchingsDetailed(
        matchings_with_score,
        score_dict,
        compatible_blood_dict,
        detailed_compatibility_index_dict,
        antibody_matches_dict,
        database_pairing_result.matchings.found_matchings_count,
        database_pairing_result.matchings.all_matchings_found
    )


def get_latest_matchings_detailed(txm_event: TxmEvent) -> MatchingsDetailed:
    maybe_config_model = get_latest_config_model_for_txm_event(txm_event.db_id)
    if maybe_config_model is None:
        raise AssertionError('There are no latest matchings in the database, '
                             "didn't you forget to call solve_from_configuration()?")
    configuration_db_id = maybe_config_model.id
    return get_matchings_detailed_for_configuration(txm_event, configuration_db_id)


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
        matchings: List[MatchingWithScore]
) -> CalculatedMatchingsDTO:
    """
    Method that creates common DTOs for FE and reports.
    """
    return CalculatedMatchingsDTO(
        calculated_matchings=[MatchingDTO(
            rounds=[
                RoundDTO(
                    transplants=[
                        TransplantDTOOut(
                            score=latest_matchings_detailed.scores_tuples[(pair.donor.db_id, pair.recipient.db_id)],
                            compatible_blood=latest_matchings_detailed.blood_compatibility_tuples[
                                (pair.donor.db_id, pair.recipient.db_id)],
                            donor=pair.donor.medical_id,
                            recipient=pair.recipient.medical_id,
                            detailed_score_per_group=get_detailed_score(
                                latest_matchings_detailed.detailed_score_tuples[
                                    (pair.donor.db_id, pair.recipient.db_id)],
                                latest_matchings_detailed.antibody_matches_tuples[
                                    (pair.donor.db_id, pair.recipient.db_id)]
                            )
                        ) for pair in matching_round.donor_recipient_pairs], )
                for matching_round in matching.get_rounds()],
            countries=matching.get_country_codes_counts(),
            score=matching.score(),
            order_id=matching.order_id(),
            count_of_transplants=get_count_of_transplants(matching)
        ) for matching in matchings
        ],
        found_matchings_count=latest_matchings_detailed.found_matchings_count,
        all_matchings_found=latest_matchings_detailed.all_matchings_found

    )
