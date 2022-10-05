from dataclasses import dataclass
from typing import Dict, Iterable, List

import networkx as nx
import numpy as np

from txmatching.configuration.config_parameters import ConfigParameters
from txmatching.patients.patient import Donor, DonorType, Recipient
from txmatching.patients.patient_types import DonorDbId, RecipientDbId
from txmatching.scorers.score_matrix import ScoreMatrix
from txmatching.scorers.scorer_from_config import scorer_from_configuration
from txmatching.utils.country_enum import Country


# pylint: disable=too-many-instance-attributes
@dataclass(init=False)
class DataAndConfigurationForILPSolver:
    non_directed_donors: Iterable[int]
    regular_donors: Iterable[int]
    configuration: ConfigParameters
    country_codes_dict: Dict[int, Country]
    required_patients: List[List[int]]
    recipient_to_donors_enum_dict: Dict[int, List[int]]
    active_and_valid_recipients_list: List[Recipient]
    active_and_valid_donors_list: List[Donor]
    donor_enum_to_related_recipient: Dict[int, int]
    graph: nx.Graph

    def __init__(self, active_and_valid_donors_dict: Dict[DonorDbId, Donor],
                 active_and_valid_recipients_dict: Dict[RecipientDbId, Recipient],
                 config_parameters: ConfigParameters):

        self.configuration = config_parameters
        self.non_directed_donors = [i for i, donor in enumerate(active_and_valid_donors_dict.values()) if
                                    donor.donor_type != DonorType.DONOR]

        donor_id_to_enum = {donor.db_id: i for i, donor in enumerate(active_and_valid_donors_dict.values())}

        self.recipient_to_donors_enum_dict = {}
        for recipient_db_id, recipient in active_and_valid_recipients_dict.items():
            donors_list = [donor_id_to_enum[donor_db_id] for donor_db_id in recipient.related_donors_db_ids if
                           donor_db_id in active_and_valid_donors_dict]
            self.recipient_to_donors_enum_dict[recipient_db_id] = donors_list

        self.donor_enum_to_related_recipient = {}
        for donor_db_id, donor in active_and_valid_donors_dict.items():
            self.donor_enum_to_related_recipient[donor_id_to_enum[donor_db_id]] = donor.related_recipient_db_id

        self.graph = self._create_graph(config_parameters, active_and_valid_donors_dict,
                                        active_and_valid_recipients_dict)

        self.regular_donors = set(self.graph.nodes()) - set(self.non_directed_donors)

        donor_db_id_to_idx = {donor.db_id: i for i, donor in enumerate(active_and_valid_donors_dict.values())}

        self.required_patients = []
        for recipient_db_id in config_parameters.required_patient_db_ids:
            related_donor_db_ids = []
            for related_donor_db_id in active_and_valid_recipients_dict[recipient_db_id].related_donors_db_ids:
                related_donor_db_ids += [donor_db_id_to_idx[active_and_valid_donors_dict[related_donor_db_id].db_id]]
            self.required_patients += [related_donor_db_ids]

        self.country_codes_dict = {i: donor.parameters.country_code for i, donor in
                                   enumerate(active_and_valid_donors_dict.values())}
        self.blood_groups_dict = {i: donor.parameters.blood_group for i, donor in
                                  enumerate(active_and_valid_donors_dict.values())}

        self.active_and_valid_recipients_list = list(active_and_valid_recipients_dict.values())
        self.active_and_valid_donors_list = list(active_and_valid_donors_dict.values())

    def _create_graph(self,
                      config_parameters: ConfigParameters,
                      active_and_valid_donors_dict: Dict[DonorDbId, Donor],
                      active_and_valid_recipients_dict: Dict[RecipientDbId, Recipient]) -> nx.Graph:
        donor_score_matrix = self._get_donor_score_matrix(
            config_parameters, active_and_valid_donors_dict, active_and_valid_recipients_dict)
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
            for node in range(0, len(active_and_valid_donors_dict))
        ])

        graph.add_edges_from([
            (from_node, to_node, {'weight': weight})
            for (from_node, to_node, weight) in edges
        ])
        return graph

    @staticmethod
    def _get_donor_score_matrix(config_parameters: ConfigParameters,
                                active_and_valid_donors_dict: Dict[DonorDbId, Donor],
                                active_and_valid_recipients_dict: Dict[RecipientDbId, Recipient]) -> ScoreMatrix:
        scorer = scorer_from_configuration(config_parameters)
        score_matrix = []
        for donor in active_and_valid_donors_dict.values():
            row = []
            for donor_for_recipient in active_and_valid_donors_dict.values():
                if (donor_for_recipient.related_recipient_db_id and donor.db_id != donor_for_recipient.db_id and
                        donor.related_recipient_db_id != donor_for_recipient.related_recipient_db_id):
                    recipient = active_and_valid_recipients_dict[donor_for_recipient.related_recipient_db_id]
                    score = scorer.score_transplant_including_original_tuple(donor, recipient, [donor_for_recipient])
                    row.append(score)
                else:
                    row.append(-1)
            score_matrix.append(row)

        score_matrix = np.array(score_matrix)

        return score_matrix
