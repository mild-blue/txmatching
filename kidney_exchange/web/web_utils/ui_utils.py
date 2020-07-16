from typing import Tuple, Dict


def hex_to_rgb(hexadecimal: str) -> Tuple[int, int, int]:
    hexadecimal = hexadecimal[1:]
    r = hexadecimal[0:2]
    g = hexadecimal[2:4]
    b = hexadecimal[4:6]
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
    # TODO index=len(key_values)-1? https://trello.com/c/MB2yxffW/128-improve-uiutils-see-code
    for index, item in enumerate(key_values):
        k, v = item
        if value < k:
            break

    # TODO key_values[0]?  https://trello.com/c/MB2yxffW/128-improve-uiutils-see-code
    left_value, left_color = key_values[index - 1]
    right_value, right_color = key_values[index]

    right_multiplier = (value - left_value) / (right_value - left_value)
    left_multiplier = 1 - right_multiplier

    left_rgb = hex_to_rgb(left_color)
    right_rgb = hex_to_rgb(right_color)

    mean_rgb = [int(left * left_multiplier + right * right_multiplier) for left, right in zip(left_rgb, right_rgb)]
    return rgb_to_hex(mean_rgb)


if __name__ == "__main__":
    print(color_gradient(99))
