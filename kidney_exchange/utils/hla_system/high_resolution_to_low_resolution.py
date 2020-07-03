"""
HLA system (https://en.wikipedia.org/wiki/Human_leukocyte_antigen)
Has some of the antigens similar, these similar ones seem like a one when using low resolution detection techniques.

For more info, see: https://en.wikipedia.org/wiki/History_and_naming_of_human_leukocyte_antigens
"""
from typing import List

# TODO: Confirm this table with some imunologist
# TODO: Is it a problem if donor has A23 antigen and recipient A24 antibody? (Both is A9)
low_resolution_to_high_resolution = {
    "A9": ["A23", "A24"],
    "A10": ["A25", "A26", "A34", "A66"],
    "A19": ["A29", "A30", "A31", "A32", "A33", "A74"],
    "A28": ["A68", "A69"],

    "B16": ["B38", "B39"],
    "B12": ["B44", "B45"],
    "B21": ["B49", "B50"],
    "B5": ["B51", "B52"],
    "B22": ["B54", "B55", "B56"],
    "B17": ["B57", "B58"],
    "B40": ["B60", "B61"],
    "B15": ["B62", "B63", "B75", "B76", "B77"],
    "B14": ["B64", "B65"],
    "B70": ["B71", "B72"],

    "DR5": ["DR11", "DR12"],
    "DR6": ["DR13", "DR14"],
    "DR2": ["DR15", "DR16"],
    "DR3": ["DR17", "DR18"],

    "Cw3": ["Cw9, Cw10"],

    "DQ1": ["DQ5", "DQ6"],
    "DQ3": ["DQ7", "DQ8", "DQ9", "DQ2", "DQ4"]
}

high_resolution_to_low_resolution = dict()

for low_res, high_res_list in low_resolution_to_high_resolution.items():
    for high_res in high_res_list:
        high_resolution_to_low_resolution[high_res] = low_res


def hla_low_to_high_res(low_resolution_code: str) -> List[str]:
    return low_resolution_to_high_resolution.get(low_resolution_code) or low_resolution_code


def hla_high_to_low_res(high_resolution_code: str) -> List[str]:
    return high_resolution_to_low_resolution.get(high_resolution_code) or high_resolution_code
