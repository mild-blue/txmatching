from typing import Callable, Optional

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Recipient, TxmEvent
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.scorers.scorer_constants import (HLA_SCORE,
                                                 TRANSPLANT_IMPOSSIBLE_SCORE)
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.blood_groups import blood_groups_compatible
from txmatching.utils.hla_system.compatibility_index import \
    get_detailed_compatibility_index
from txmatching.utils.hla_system.detailed_score import get_detailed_score
from txmatching.utils.hla_system.hla_crossmatch import (
    get_crossmatched_antibodies_per_group, is_positive_hla_crossmatch)
from txmatching.utils.recipient_donor_compatibility import \
    RecipientDonorsCompatibility, RecipientDonorCompatibilityDetails


# pylint: disable=too-many-locals
# Too many locals might be resolved while optimizing: https://github.com/mild-blue/txmatching/issues/1163
# pylint: disable=too-many-arguments
# All arguments are needed here.
def calculate_cpra_and_get_compatible_donors_for_recipient(txm_event: TxmEvent,
                                                           recipient: Recipient,
                                                           configuration_parameters: ConfigParameters,
                                                           compatibility_graph: Optional[CompatibilityGraph] = None,
                                                           compute_cpra: bool = False,
                                                           crossmatch_logic: Callable = get_crossmatched_antibodies_per_group) \
                -> RecipientDonorsCompatibility:
    """
    Calculates cPRA for recipient (which part of donors [as decimal] is incompatible) for txm_event and returns list of
    compatible donors optionally with details about compatibility.
    While cPRA is computed based solely on the hla crossmatch, compatible donors are computed based on the overall
    recipient-donor score.

    If the matching corresponding to `configuration_parameters` is already computed, the `compatibility_graph` is
    passed as an argument and used to skip the computation of recipient-donor score.

    :param compatibility_details: Compute details of recipient-donor compatibility if True, return only set of
        compatible donors if False.
    :param compute_cpra: Compute cpra (computationally demanding) if True.
    :return: (cpra (optional), set of compatible donors, list of compatibilities details (optional))
    """

    scorer = scorer_from_configuration(configuration_parameters)

    active_donors_dict = txm_event.active_and_valid_donors_dict

    if len(active_donors_dict) == 0:  # no donors = not compatible to the whole donor population
        return RecipientDonorsCompatibility(1, set(), None)

    compatible_donors_details = []
    compatible_donors = set()
    n_hla_crossmatch_compatible = 0

    for donor in active_donors_dict.values():

        antibodies = None

        if compute_cpra:
            # donor is compatible with the recipient (considering only hla crossmatch)
            if not is_positive_hla_crossmatch(donor_hla_typing=donor.parameters.hla_typing,
                                              recipient_antibodies=recipient.hla_antibodies,
                                              use_high_resolution=configuration_parameters.use_high_resolution,
                                              crossmatch_level=configuration_parameters.hla_crossmatch_level,
                                              crossmatch_logic=crossmatch_logic):
                n_hla_crossmatch_compatible += 1

        if compatibility_graph is None:
            original_donors = [active_donors_dict[donor_db_id] for
                           donor_db_id in recipient.related_donors_db_ids if donor_db_id in active_donors_dict]
            score = scorer.score_transplant(donor, recipient, original_donors)
        else:
            d_r_id_pair = (donor.db_id, recipient.db_id)
            if d_r_id_pair in compatibility_graph.keys():
                score = compatibility_graph[d_r_id_pair][HLA_SCORE]
            else:
                score = None

        if score and score > TRANSPLANT_IMPOSSIBLE_SCORE:
            compatible_donors.add(donor.db_id)

            # Do not compute compatibility details with the original donor
            if donor.related_recipient_db_id != recipient.db_id:
                compatibility_index_detailed = get_detailed_compatibility_index(
                    donor_hla_typing=donor.parameters.hla_typing,
                    recipient_hla_typing=recipient.parameters.hla_typing,
                    ci_configuration=scorer.ci_configuration
                )
                antibodies = crossmatch_logic(
                    donor.parameters.hla_typing,
                    recipient.hla_antibodies,
                    configuration_parameters.use_high_resolution)
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
    return RecipientDonorsCompatibility(cpra, compatible_donors, compatible_donors_details)
