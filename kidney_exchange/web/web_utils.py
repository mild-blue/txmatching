from typing import List, Tuple, Dict

from kidney_exchange.patients.donor import Donor
from kidney_exchange.patients.recipient import Recipient

# TODO: Zjistit, kde jsou následující importy
from transplant_matching.core.transplant_scorers.compatibility_index import _get_matches_count, _get_locus_antigens
from transplant_matching.core.transplant_scorers.hla_system import get_simplified_classification
from transplant_matching.utils.patient_naming import get_country


def common_antigens(donor: Donor, recipient: Recipient, group: str = None) -> Tuple[List[str], int]:
    locus_antigens = [_get_locus_antigens(antigens, group)
                      for antigens in [donor.hla_antigens, recipient.hla_antigens]]

    donor_simplified_antigens, recipient_simplified_antigens = [
        [get_simplified_classification(antigen) for antigen in antigens]
        for antigens in locus_antigens]

    count = _get_matches_count(donor.hla_antigens, recipient.hla_antigens, group)

    common_antigens = list(set(donor_simplified_antigens).intersection(set(recipient_simplified_antigens)))
    common_antigens.sort()

    return (common_antigens, count)


def hex_to_rgb(hex: str) -> Tuple[int, int, int]:
    hex = hex[1:]
    r = hex[0:2]
    g = hex[2:4]
    b = hex[4:6]
    return tuple(int(v, 16) for v in (r, g, b))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    hx = [str(hex(v)[2:]) for v in rgb]
    hx = [h if len(h) == 2 else "0" + h for h in hx]
    return "#" + "".join(hx)


def color_gradient(value: float, colors: Dict = {0: "#ff8282", 50: "#ffde82", 100: "#aeff82"}) -> str:
    if value <= 0:
        value = 1

    if value >= 100:
        value = 99

    key_values = [(k, v) for k, v in colors.items()]
    key_values.sort(key=lambda item: item[0])
    for index, item in enumerate(key_values):
        k, v = item
        if value < k:
            break

    left_value, left_color = key_values[index - 1]
    right_value, right_color = key_values[index]

    right_multiplier = (value - left_value) / (right_value - left_value)
    left_multiplier = 1 - right_multiplier

    left_rgb = hex_to_rgb(left_color)
    right_rgb = hex_to_rgb(right_color)

    mean_rgb = [int(l * left_multiplier + r * right_multiplier) for l, r in zip(left_rgb, right_rgb)]
    return rgb_to_hex(mean_rgb)


def name_to_flag_path(patient_name: str) -> str:
    return "static/img/countries/" + get_country(patient_name) + ".png"


if __name__ == "__main__":
    print(color_gradient(99))
