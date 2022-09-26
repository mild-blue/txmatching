from typing import Dict, List, Optional

from txmatching.configuration.config_parameters import (
    ConfigParameters, ManualDonorRecipientScore)
from txmatching.patients.patient import Donor, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.compatibility_graph import CompatibilityGraph
from txmatching.scorers.scorer_base import ScorerBase
from txmatching.scorers.scorer_constants import ORIGINAL_DONOR_RECIPIENT_SCORE
from txmatching.solvers.matching.matching import Matching
from txmatching.utils.hla_system.compatibility_index import CIConfiguration


class AdditiveScorer(ScorerBase):
    def __init__(self, manual_donor_recipient_scores: List[ManualDonorRecipientScore] = None):
        if manual_donor_recipient_scores is not None:
            self._manual_donor_recipient_scores = {
                (don_rec_score.donor_db_id, don_rec_score.recipient_db_id): don_rec_score.score
                for don_rec_score in manual_donor_recipient_scores}
        else:
            self._manual_donor_recipient_scores = {}

    def score_transplant(self, donor: Donor, recipient: Recipient, original_donors: Optional[List[Donor]]) -> float:
        manual_score = self._manual_donor_recipient_scores.get((donor.db_id, recipient.db_id))
        if manual_score is None:
            return self.score_transplant_calculated(donor, recipient, original_donors)
        else:
            return self.get_score_when_manual_score_set(manual_score)

    def score_transplant_calculated(self, donor: Donor, recipient: Recipient,
                                    original_donors: Optional[List[Donor]]) -> float:
        raise NotImplementedError('Has to be overridden')

    def get_score_when_manual_score_set(self, manual_score) -> float:
        raise NotImplementedError('Has to be overridden')

    def score(self, matching: Matching, donors_dict: Dict[DonorDbId, Donor],
              recipients_dict: Dict[RecipientDbId, Recipient]) -> float:
        """
        Higher score means better matching
        """
        total_score = 0
        for transplant in matching.get_donor_recipient_pairs():
            donor, recipient = transplant
            original_donors = [donors_dict[donor_db_id] for donor_db_id in recipient.related_donors_db_ids if
                               donor_db_id in donors_dict]
            total_score += self.score_transplant(donor=donor, recipient=recipient,
                                                 original_donors=original_donors)

        return total_score

    def get_donor_idx_to_recipient_idx(self,
                                       recipients_dict: Dict[RecipientDbId, Recipient],
                                       donors_dict: Dict[DonorDbId, Donor]) -> Dict[int, int]:
        donor_idx_to_recipient_idx = {donor_enum: recipient_enum for recipient_enum, recipient in
                                      enumerate(recipients_dict.values()) for donor_enum, donor in
                                      enumerate(donors_dict.values()) if donor.related_recipient_db_id == recipient.db_id}
        for donor_enum, _ in enumerate(donors_dict.values()):
            if donor_enum not in donor_idx_to_recipient_idx:
                donor_idx_to_recipient_idx[donor_enum] = -1
        return donor_idx_to_recipient_idx

    def get_compatibility_graph(self,
                                recipients_dict: Dict[RecipientDbId, Recipient],
                                donors_dict: Dict[DonorDbId, Donor]) -> CompatibilityGraph:
        '''the compatibility graph has structure (new_donor_inex, new_recipient_index): score'''

        compatibility_graph = {}

        for donor_enum, donor in enumerate(donors_dict.values()):
            for recipient_enum, recipient in enumerate(recipients_dict.values()):
                score = self.score_transplant_including_original_tuple(donor=donor, recipient=recipient,
                                                                       original_donors=[donors_dict[donor_db_id] for
                                                                       donor_db_id in recipient.related_donors_db_ids
                                                                       if donor_db_id in donors_dict])
                if score >= 0:
                    compatibility_graph[(donor_enum, recipient_enum)] = score

        return compatibility_graph

    def get_score_dict(self, recipients_dict: Dict[RecipientDbId, Recipient], donors_dict: Dict[DonorDbId, Donor],
                       compatibility_graph: CompatibilityGraph) -> CompatibilityGraph:
        score_dict = {}
        for donor_enum, donor_id in enumerate(donors_dict.keys()):
            for recipient_enum, recipient_id in enumerate(recipients_dict.keys()):
                if (donor_enum, recipient_enum) in compatibility_graph:
                    score_dict[(donor_id, recipient_id)] = compatibility_graph[(donor_enum, recipient_enum)]
        return score_dict

    def score_transplant_including_original_tuple(self, donor: Donor, recipient: Recipient,
                                                  original_donors: List[Donor]) -> float:
        if donor.db_id in recipient.related_donors_db_ids:
            score = ORIGINAL_DONOR_RECIPIENT_SCORE
        else:
            score = self.score_transplant(donor, recipient, original_donors)
        return score

    @classmethod
    def from_config(cls, config_parameters: ConfigParameters) -> 'AdditiveScorer':
        raise NotImplementedError('Has to be overridden')

    @property
    def ci_configuration(self) -> CIConfiguration:
        raise NotImplementedError('Has to be overridden')

    @property
    def max_transplant_score(self) -> float:
        raise NotImplementedError('Has to be overridden')
