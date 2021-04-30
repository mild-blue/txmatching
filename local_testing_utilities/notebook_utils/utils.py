import re


def parse_hla(hla_codes_str: str) -> str:
    if 'neg' in hla_codes_str.lower():
        return ''
    # remove codes in brackets, they are only in detail all the split codes for broade in front of the bracket
    hla_codes_str = re.sub(r'\(.*?\)', '', hla_codes_str)
    hla_codes = re.split('[,. ()]+', hla_codes_str)
    hla_codes = [code.upper() for code in hla_codes if len(code) > 0]

    return ' '.join(sorted(hla_codes))


def parse_acceptable_blood(acceptable_blood: str) -> str:
    blood_groups = re.split('[, ]+', acceptable_blood)

    if len(blood_groups) == 1 and blood_groups[0] == '':
        return ''

    if not all([(blood_group in ['A', 'B', 'AB', '0']) for blood_group in blood_groups]):
        raise ValueError(f'Invalid blood group ({acceptable_blood})')

    return ' '.join(sorted(blood_groups))
