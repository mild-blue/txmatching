from dataclasses import dataclass
from typing import Dict, Iterable, List

import networkx as nx

from txmatching.configuration.configuration import Configuration
from txmatching.patients.patient import Donor, DonorType, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.country_enum import Country


@dataclass(init=False)
class DataAndConfigurationForILPSolver:
    non_directed_donors: Iterable[int]
    regular_donors: Iterable[int]
    configuration: Configuration
    country_codes_dict: Dict[int, Country]
    required_patients: List[int]
    graph: nx.Graph

    def __init__(self, active_donors_dict: Dict[DonorDbId, Donor],
                 active_recipients_dict: Dict[RecipientDbId, Recipient],
                 configuration: Configuration):

        self.configuration = configuration
        self.non_directed_donors = [i for i, donor in enumerate(active_donors_dict.values()) if
                                    donor.donor_type != DonorType.DONOR]
        self.graph = self._create_graph(configuration, active_donors_dict, active_recipients_dict)

        self.regular_donors = set(self.graph.nodes()) - set(self.non_directed_donors)

        donor_db_id_to_idx = {donor.db_id: i for i, donor in enumerate(active_donors_dict.values())}
        self.required_patients = [donor_db_id_to_idx[
                                      active_donors_dict[
                                          active_recipients_dict[recipient_db_id].related_donor_db_id].db_id]
                                  for
                                  recipient_db_id in configuration.required_patient_db_ids]

        self.country_codes_dict = {i: donor.parameters.country_code for i, donor in
                                   enumerate(active_donors_dict.values())}
        self.blood_groups_dict = {i: donor.parameters.blood_group for i, donor in
                                  enumerate(active_donors_dict.values())}

    def _create_graph(self,
                      configuration: Configuration,
                      active_donors_dict: Dict[DonorDbId, Donor],
                      active_recipients_dict: Dict[RecipientDbId, Recipient]) -> nx.Graph:

        donor_score_matrix = self._get_donor_score_matrix(configuration, active_donors_dict, active_recipients_dict)
        num_nodes = len(donor_score_matrix)
        edges = []
        for from_node in range(0, num_nodes):
            for to_node in range(0, num_nodes):
                weight = int(donor_score_matrix[from_node][to_node])
                if weight >= 0:
                    edges.append((from_node, to_node, weight))
        graph = nx.DiGraph()

        graph.add_nodes_from([
            (node, {'ndd': node in self.non_directed_donors})
            for node in range(0, len(active_donors_dict))
        ])

        graph.add_edges_from([
            (from_node, to_node, {'weight': weight})
            for (from_node, to_node, weight) in edges
        ])
        return graph

    @staticmethod
    def _get_donor_score_matrix(configuration: Configuration,
                                active_donors_dict: Dict[DonorDbId, Donor],
                                active_recipients_dict: Dict[RecipientDbId, Recipient]):
        scorer = scorer_from_configuration(configuration)
        score_matrix = []
        for donor in active_donors_dict.values():
            row = []
            for donor_for_recipient in active_donors_dict.values():

                if donor_for_recipient.related_recipient_db_id and donor.db_id != donor_for_recipient.db_id:
                    recipient = active_recipients_dict[donor_for_recipient.related_recipient_db_id]
                    score = scorer.score_transplant_including_original_tuple(donor, recipient, donor_for_recipient)
                    row.append(score)
                else:
                    row.append(-1)

            score_matrix.append(row)
        return score_matrix
