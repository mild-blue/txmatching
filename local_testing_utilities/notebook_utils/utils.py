import re


def parse_hla(hla_codes_str: str) -> str:
    if 'neg' in hla_codes_str.lower():
        return ''
    # remove codes in brackets, they are only in detail all the split codes for broade in front of the bracket
    hla_codes_str = re.sub(r'\(.*?\)', '', hla_codes_str)
    hla_codes = re.split('[,. ()]+', hla_codes_str)
    hla_codes = [code.upper() for code in hla_codes if len(code) > 0]

    return ' '.join(sorted(hla_codes))
