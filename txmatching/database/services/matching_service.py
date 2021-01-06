import dataclasses
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from dacite import from_dict

from txmatching.data_transfer_objects.matchings.calculated_matchings_dto import \
    CalculatedMatchingsDTO
from txmatching.data_transfer_objects.matchings.matching_dto import (
    MatchingDTO, RoundDTO, TransplantDTOOut)
from txmatching.data_transfer_objects.patients.out_dots.conversions import \
    get_detailed_score
from txmatching.database.services.config_service import (
    get_config_model_for_txm_event, get_configuration_for_txm_event)
from txmatching.database.services.txm_event_service import get_txm_event
from txmatching.database.sql_alchemy_schema import PairingResultModel
from txmatching.patients.patient import Donor, Recipient
from txmatching.scorers.matching import get_count_of_transplants
from txmatching.solvers.donor_recipient_pair import DonorRecipientPair
from txmatching.solvers.matching.matching_with_score import MatchingWithScore
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import (
    DetailedCompatibilityIndexForHLAGroup, get_detailed_compatibility_index)
from txmatching.utils.hla_system.hla_crossmatch import (
    AntibodyMatchForHLAGroup, get_crossmatched_antibodies)


@dataclass
class LatestMatchingsDetailed:
    matchings: List[MatchingWithScore]
    scores_tuples: Dict[Tuple[int, int], float]
    blood_compatibility_tuples: Dict[Tuple[int, int], bool]
    detailed_score_tuples: Dict[Tuple[int, int], List[DetailedCompatibilityIndexForHLAGroup]]
    antibody_matches_tuples: Dict[Tuple[int, int], List[AntibodyMatchForHLAGroup]]


def get_latest_matchings_detailed(txm_event_db_id: int) -> LatestMatchingsDetailed:
    maybe_config_model = get_config_model_for_txm_event(txm_event_db_id)
    if maybe_config_model is None:
        raise AssertionError('There are no latest matchings in the database, '
                             "didn't you forget to call solve_from_configuration()?")
    configuration = get_configuration_for_txm_event(txm_event_db_id)
    configuration_id = maybe_config_model.id
    last_pairing_result_model = (
        PairingResultModel
            .query.filter(PairingResultModel.config_id == configuration_id)
            .first()
    )

    if last_pairing_result_model is None:
        raise AssertionError('There are no latest matchings in the database, '
                             "didn't you forget to call solve_from_configuration()?")

    txm_event = get_txm_event(txm_event_db_id)

    calculated_matchings = from_dict(data_class=CalculatedMatchingsDTO,
                                     data=last_pairing_result_model.calculated_matchings)

    all_matchings = _db_matchings_to_matching_list(calculated_matchings, txm_event.active_donors_dict,
                                                   txm_event.active_recipients_dict)

    score_matrix = last_pairing_result_model.score_matrix['score_matrix_dto']
    score_dict = {
        (donor_db_id, recipient_db_id): score for donor_db_id, row in
        zip(txm_event.active_donors_dict, score_matrix) for recipient_db_id, score in
        zip(txm_event.active_recipients_dict, row)
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

    return LatestMatchingsDetailed(
        all_matchings,
        score_dict,
        compatible_blood_dict,
        detailed_compatibility_index_dict,
        antibody_matches_dict
    )


def _db_matchings_to_matching_list(
        calculated_matchings: CalculatedMatchingsDTO,
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


def create_matching_dtos(
        latest_matchings_detailed: LatestMatchingsDetailed,
        matchings: List[MatchingWithScore]
) -> List[Union[tuple, dict]]:
    """
    Method that creates common DTOs for FE and reports.
    """
    return [
        dataclasses.asdict(MatchingDTO(
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
        )) for matching in matchings
    ]
