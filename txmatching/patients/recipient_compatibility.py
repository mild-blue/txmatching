from typing import Callable, List, Optional, Set, Tuple

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Recipient, TxmEvent
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.scorers.scorer_constants import TRANSPLANT_IMPOSSIBLE_SCORE
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import \
    get_detailed_compatibility_index
from txmatching.utils.hla_system.detailed_score import get_detailed_score
from txmatching.utils.hla_system.hla_crossmatch import \
    get_crossmatched_antibodies_per_group
from txmatching.utils.recipient_donor_compatibility_details import \
    RecipientDonorCompatibilityDetails


# pylint: disable=too-many-locals
# Too many locals might be resolved while optimizing: https://github.com/mild-blue/txmatching/issues/1163
# pylint: disable=too-many-arguments
# All arguments are needed here.
def calculate_cpra_and_get_compatible_donors_for_recipient(txm_event: TxmEvent,
                                                           recipient: Recipient,
                                                           configuration: Configuration,
                                                           compatibility_graph: Optional[CompatibilityGraph] = None,
                                                           compute_compatibility_details: bool = False,
                                                           compute_cpra: bool = False,
                                                           crossmatch_logic: Callable = get_crossmatched_antibodies_per_group) \
                -> Tuple[Optional[int], Set[int], Optional[List[RecipientDonorCompatibilityDetails]]]:
    """
    Calculates cPRA for recipient (which part of donors [as decimal] is incompatible) for txm_event and returns list of
    compatible donors optionally with details about compatibility.
    While cPRA is computed based solely on the hla crossmatch, compatible donors are computed based on the overall
    recipient-donor score.

    :param compatibility_details: Compute details of recipient-donor compatibility if True, return only set of
        compatible donors if False.
    :return: (cpra, set of compatible donors, list of compatibilities details (optional) )
    """

    scorer = scorer_from_configuration(configuration.parameters)

    active_donors_dict = txm_event.active_and_valid_donors_dict

    if len(active_donors_dict) == 0:  # no donors = not compatible to the whole donor population
        return 1, set(), []

    compatible_donors_details = []
    compatible_donors = set()
    n_hla_crossmatch_compatible = 0

    for donor in active_donors_dict.values():

        antibodies = None

        if compute_cpra:
            # TODO - duplicity with `is_hla_crossmatch()`, should be resolved in https://github.com/mild-blue/txmatching/issues/1163,
            # or https://github.com/mild-blue/txmatching/issues/1160
            antibodies = crossmatch_logic(
                donor.parameters.hla_typing,
                recipient.hla_antibodies,
                configuration.parameters.use_high_resolution)
            common_codes = {antibody_match.hla_antibody for antibody_match_group in antibodies
                            for antibody_match in antibody_match_group.antibody_matches
                            if antibody_match.match_type.is_positive_for_level(configuration.parameters.hla_crossmatch_level)}

            if len(common_codes) == 0: # donor is compatible with the recipient (considering only hla crossmatch)
                n_hla_crossmatch_compatible += 1

        if compatibility_graph is None:
            original_donors = [active_donors_dict[donor_db_id] for
                           donor_db_id in recipient.related_donors_db_ids if donor_db_id in active_donors_dict]
            score = scorer.score_transplant(donor, recipient, original_donors)
        else:
            d_r_id_pair = (donor.db_id, recipient.db_id)
            if d_r_id_pair in compatibility_graph.keys():
                score = compatibility_graph[d_r_id_pair]['hla_compatibility_score']
            else:
                score = None

        if score and score > TRANSPLANT_IMPOSSIBLE_SCORE:
            compatible_donors.add(donor.db_id)

            # Do not compute compatibility details with the original donor
            if compute_compatibility_details and (donor.related_recipient_db_id != recipient.db_id):
                compatibility_index_detailed = get_detailed_compatibility_index(
                    donor_hla_typing=donor.parameters.hla_typing,
                    recipient_hla_typing=recipient.parameters.hla_typing,
                    ci_configuration=scorer.ci_configuration
                )
                if antibodies is None:
                    antibodies = crossmatch_logic(
                        donor.parameters.hla_typing,
                        recipient.hla_antibodies,
                        configuration.parameters.use_high_resolution)
                detailed_score = get_detailed_score(compatibility_index_detailed, antibodies)

                recipient_donor_compatibility_details = RecipientDonorCompatibilityDetails(
                    recipient_db_id=recipient.db_id,
                    donor_db_id=donor.db_id,
                    score=score,
                    max_score=scorer.max_transplant_score,
                    compatible_blood=blood_groups_compatible(
                            donor.parameters.blood_group, recipient.parameters.blood_group),
                    detailed_score=detailed_score
                )

                compatible_donors_details.append(recipient_donor_compatibility_details)

    cpra = 1 - n_hla_crossmatch_compatible / len(active_donors_dict) if compute_cpra else None
    compatible_donors_details = compatible_donors_details if compute_compatibility_details else None
    return cpra, compatible_donors, compatible_donors_details
