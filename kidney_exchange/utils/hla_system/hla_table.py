# HLA system (https://en.wikipedia.org/wiki/Human_leukocyte_antigen)
# Has some of the antigens similar, these similar ones seem like a one when using broad resolution detection techniques.
#
# For more info, see: https://en.wikipedia.org/wiki/History_and_naming_of_human_leukocyte_antigens

# TODO: Confirm this table with some immunologist https://trello.com/c/MtiTnNYG
# TODO: ask what exact antigens should I count in the matches - for example what about DR52, DR53 - what do those mean
#  https://trello.com/c/08MZVRCk
# TODO: Is it a problem if donor has A23 antigen and recipient A24 antibody? (Both is A9) https://trello.com/c/UIo23mPb
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)
HLA_A = ["A1", "A2", "A203", "A210", "A3", "A11", "A23", "A24", "A2403",
         "A25", "A26", "A29", "A30", "A31", "A32", "A33", "A34", "A36",
         "A43", "A66", "A68", "A69", "A74", "A80"]

HLA_A_BROAD = ["A9", "A10", "A19", "A28"]

HLA_B = ["B7", "B703", "B8", "B13", "B18", "B27", "B2708", "B35", "B37",
         "B38", "B39", "B3901", "B3902", "B4005", "B41", "B42", "B44",
         "B45", "B46", "B47", "B48", "B49", "B50", "B51", "B5102", "B5103",
         "B52", "B53", "B54", "B55", "B56", "B57", "B58", "B59", "B60",
         "B61", "B62", "B63", "B64", "B65", "B67", "B71", "B72", "B73",
         "B75", "B76", "B77", "B78", "B81", "B82"]

HLA_B_BROAD = ["B5", "B12", "B14", "B15", "B16", "B17", "B22", "B40", "B70"]

HLA_BW = ["Bw4", "Bw6"]

HLA_CW = ["Cw1", "Cw2", "Cw4", "Cw5", "Cw6", "Cw7", "Cw8", "Cw9", "Cw10"]

HLA_CW_BROAD = ["Cw3"]

HLA_DR = ["DR1", "DR103", "DR4", "DR7", "DR8", "DR9", "DR10", "DR11", "DR12",
          "DR13", "DR14", "DR1403", "DR1404", "DR15", "DR16", "DR17", "DR18"]

HLA_DR_BROAD = ["DR2", "DR3", "DR5", "DR6"]

HLA_DRDR = ["DR51", "DR52", "DR53"]

HLA_DQ = ["DQ2", "DQ4", "DQ5", "DQ6", "DQ7", "DQ8", "DQ9"]

HLA_DQ_BROAD = ["DQ1", "DQ3"]

split_to_broad = {"A23": "A9",
                  "A24": "A9",
                  "A25": "A10",
                  "A26": "A10",
                  "A29": "A19",
                  "A30": "A19",
                  "A31": "A19",
                  "A32": "A19",
                  "A33": "A19",
                  "A34": "A10",
                  "A66": "A10",
                  "A68": "A28",
                  "A69": "A28",
                  "A74": "A19",
                  "B38": "B16",
                  "B39": "B16",
                  "B44": "B12",
                  "B45": "B12",
                  "B49": "B21",
                  "B50": "B21",
                  "B51": "B5",
                  "B52": "B5",
                  "B54": "B22",
                  "B55": "B22",
                  "B56": "B22",
                  "B57": "B17",
                  "B58": "B17",
                  "B60": "B40",
                  "B61": "B40",
                  "B62": "B15",
                  "B63": "B15",
                  "B64": "B14",
                  "B65": "B14",
                  "B71": "B70",
                  "B72": "B70",
                  "B75": "B15",
                  "B76": "B15",
                  "B77": "B15",
                  "Cw9": "Cw3",
                  "Cw10": "Cw3",
                  "DR11": "DR5",
                  "DR12": "DR5",
                  "DR13": "DR6",
                  "DR14": "DR6",
                  "DR15": "DR2",
                  "DR16": "DR2",
                  "DR17": "DR3",
                  "DR18": "DR3",
                  "DQ5": "DQ1",
                  "DQ6": "DQ1",
                  "DQ7": "DQ3",
                  "DQ8": "DQ3",
                  "DQ9": "DQ3"
                  }

broad_to_split = dict()
for split, broad in split_to_broad.items():
    if broad not in broad_to_split:
        broad_to_split[broad] = list()

    broad_to_split[broad].append(split)


def is_split(antigen_code: str) -> Optional[bool]:
    """
    Return if antigen code is split, broad or we don't know = None
    :param antigen_code:
    :return:
    """
    split_codes = HLA_A + HLA_B + HLA_BW + HLA_CW + HLA_DR + HLA_DRDR + HLA_DQ_BROAD
    broad_codes = HLA_A_BROAD + HLA_B_BROAD + HLA_CW_BROAD + HLA_DR_BROAD

    if antigen_code in split_codes:
        return True

    if antigen_code in broad_codes:
        return False

    return None


def hla_split_to_broad(split_code: str) -> str:
    return split_to_broad.get(split_code) or split_code


HLA_A_broad = list(map(hla_split_to_broad, HLA_A))
HLA_B_broad = list(map(hla_split_to_broad, HLA_B))
HLA_DR_broad = list(map(hla_split_to_broad, HLA_DR))


def is_valid_broad_code(code: str) -> bool:
    for code_list in [HLA_A_broad, HLA_B_broad, HLA_DR_broad]:
        if code in code_list:
            return True

    return False
