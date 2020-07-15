import os
from typing import List, Tuple

from kidney_exchange.patients.donor import Donor, DonorDto
from kidney_exchange.patients.recipient import Recipient, RecipientDto
from kidney_exchange.scorers.hla_additive_scorer import HLAAdditiveScorer
from kidney_exchange.solvers.all_solutions_solver import AllSolutionsSolver
from kidney_exchange.utils.excel_parsing.parse_excel_data import parse_excel_data


def _get_donors_recipients(donor_dtos: List[DonorDto], recipient_dtos: List[RecipientDto]) \
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
    excel_path = os.environ.get("PATIENT_DATA_PATH")
    donors_raw, recipients_raw = parse_excel_data(excel_path)
    donors, recipients = _get_donors_recipients(donors_raw, recipients_raw)

    scorer = HLAAdditiveScorer(enforce_compatible_blood_group=False,
                               minimum_compatibility_index=0,
                               require_new_donor_having_better_match_in_compatibility_index_or_blood_group=False,
                               require_new_donor_having_better_match_in_compatibility_index=False,
                               use_binary_scoring=False)

    solver = AllSolutionsSolver()
    matching_iterator = solver.solve(donors=donors, recipients=recipients, scorer=scorer)

    print("[INFO] Looking for matchings")
    matchings = list(matching_iterator)
    print("    -- done")

    print("[INFO] Scoring matchings")
    matching_scores = [
        sum(scorer.score_transplant(donor, recipient) for donor, recipient in matching.donor_recipient_list)
        for matching in matchings]
    print("    -- done")

    print("[INFO] Sorting matchings")
    scored_matchings = list(zip(matchings, matching_scores))
    scored_matchings.sort(key=lambda matching_score: matching_score[1], reverse=True)
    print("    -- done")

    for matching, score in scored_matchings[:10]:
        print(score)
        print(matching)
