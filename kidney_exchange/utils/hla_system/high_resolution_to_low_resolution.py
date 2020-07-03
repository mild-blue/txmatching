from typing import List

from kidney_exchange.utils.hla_system.hla_table import high_resolution_to_low_resolution, HLA_A, HLA_B, HLA_DR


def hla_high_to_low_res(high_resolution_code: str) -> List[str]:
    return high_resolution_to_low_resolution.get(high_resolution_code) or high_resolution_code


HLA_A_low_res = list(map(hla_high_to_low_res, HLA_A))
HLA_B_low_res = list(map(hla_high_to_low_res, HLA_B))
HLA_DR_low_res = list(map(hla_high_to_low_res, HLA_DR))


def is_valid_low_res_code(code: str) -> bool:
    for code_list in [HLA_A_low_res, HLA_B_low_res, HLA_DR_low_res]:
        if code in code_list:
            return True

    return False


if __name__ == "__main__":
    code = "B38"
    low_res_code = hla_high_to_low_res(code)
    print(f"Low res code: {low_res_code} [is valid: {is_valid_low_res_code(low_res_code)}]")

    print(HLA_B_low_res)
    print(HLA_B_low_res)
    print(HLA_DR_low_res)
