import logging
import os
import sys
from typing import List, Tuple

from kidney_exchange.patients.donor import Donor
from kidney_exchange.web.data_transfer_objects.patient_dtos.donor_dto import DonorDTO
from kidney_exchange.patients.recipient import Recipient
from kidney_exchange.web.data_transfer_objects.patient_dtos.recipient_dto import RecipientDTO
from kidney_exchange.scorers.hla_additive_scorer import HLAAdditiveScorer
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data

logger = logging.getLogger(__name__)


def _get_donors_recipients(donor_dtos: List[DonorDTO], recipient_dtos: List[RecipientDTO]) \
        -> Tuple[List[Donor], List[Recipient]]:
    donors = [Donor(db_id=hash(donor.medical_id),
                    medical_id=donor.medical_id,
                    parameters=donor.parameters)
              for donor in donor_dtos]
    recipients = [Recipient(db_id=hash(recipient.medical_id),
                            medical_id=recipient.medical_id,
                            parameters=recipient.parameters,
                            related_donor=donors[donor_dtos.index(recipient.related_donor)])
                  for recipient in recipient_dtos]
    return donors, recipients


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
                        stream=sys.stdout)
    excel_path = os.environ.get("PATIENT_DATA_PATH")
    donors_raw, recipients_raw = parse_excel_data(excel_path)
    main_donors, main_recipients = _get_donors_recipients(donors_raw, recipients_raw)

    scorer = HLAAdditiveScorer(enforce_compatible_blood_group=False,
                               minimum_total_score=0.0,
                               require_new_donor_having_better_match_in_compatibility_index_or_blood_group=False,
                               require_new_donor_having_better_match_in_compatibility_index=False,
                               use_binary_scoring=False)

    solver = AllSolutionsSolver()
    matching_iterator = solver.solve(donors=main_donors, recipients=main_recipients, scorer=scorer)

    logger.info("Looking for matchings")
    matchings = list(matching_iterator)
    logger.info("    -- done")

    logger.info("Scoring matchings")
    matching_scores = [
        sum(scorer.score_transplant(donor, recipient) for donor, recipient in matching.donor_recipient_list)
        for matching in matchings]
    matching_round_counts = [len(matching.get_rounds()) for matching in matchings]
    matching_patients_involved = [len(matching.donor_recipient_list) for matching in matchings]
    logger.info("    -- done")

    logger.info("Sorting matchings")
    scored_matchings = list(zip(matchings, matching_round_counts, matching_patients_involved, matching_scores))
    for criterion_index in [1, 3, 2]:
        scored_matchings.sort(key=lambda matching_score: matching_score[criterion_index], reverse=True)
    logger.info("    -- done")

    for matching, round_count, patient_count, score in scored_matchings[:10]:
        rounds_str = "  ".join([f"[{str(transplant_round)}]" for transplant_round in matching.get_rounds()])
        str_repr = f"{patient_count}/{round_count} ({score}):  {rounds_str}"
        logger.info(str_repr)
