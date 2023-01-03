from typing import Set, Union

from txmatching.utils.hla_system.hla_regexes import try_convert_ultra_high_res
from txmatching.utils.hla_system.hla_transformations.parsing_issue_detail import \
    ParsingIssueDetail
from txmatching.utils.hla_system.rel_dna_ser_parsing import (
    PATH_TO_REL_DNA_SER, parse_rel_dna_ser)

# the dict below is based on http://hla.alleles.org/antigens/recognised_serology.html

SPLIT_TO_BROAD = {'A23': 'A9',
                  'A24': 'A9',
                  'A25': 'A10',
                  'A26': 'A10',
                  'A29': 'A19',
                  'A30': 'A19',
                  'A31': 'A19',
                  'A32': 'A19',
                  'A33': 'A19',
                  'A34': 'A10',
                  'A66': 'A10',
                  'A68': 'A28',
                  'A69': 'A28',
                  'A74': 'A19',
                  'B38': 'B16',
                  'B39': 'B16',
                  'B44': 'B12',
                  'B45': 'B12',
                  'B49': 'B21',
                  'B50': 'B21',
                  'B51': 'B5',
                  'B52': 'B5',
                  'B54': 'B22',
                  'B55': 'B22',
                  'B56': 'B22',
                  'B57': 'B17',
                  'B58': 'B17',
                  'B60': 'B40',
                  'B61': 'B40',
                  'B62': 'B15',
                  'B63': 'B15',
                  'B64': 'B14',
                  'B65': 'B14',
                  'B71': 'B70',
                  'B72': 'B70',
                  'B75': 'B15',
                  'B76': 'B15',
                  'B77': 'B15',
                  'CW9': 'CW3',
                  'CW10': 'CW3',
                  'DR11': 'DR5',
                  'DR12': 'DR5',
                  'DR13': 'DR6',
                  'DR14': 'DR6',
                  'DR15': 'DR2',
                  'DR16': 'DR2',
                  'DR17': 'DR3',
                  'DR18': 'DR3',
                  'DQ5': 'DQ1',
                  'DQ6': 'DQ1',
                  'DQ7': 'DQ3',
                  'DQ8': 'DQ3',
                  'DQ9': 'DQ3'
                  }


_get_high_res_or_ultra_high_res = lambda ultra_high_res: try_convert_ultra_high_res(ultra_high_res) \
                                                         or ultra_high_res


PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS = parse_rel_dna_ser(PATH_TO_REL_DNA_SER)
ALL_HIGH_RES_CODES = set(parse_rel_dna_ser(PATH_TO_REL_DNA_SER).split.to_dict().keys())
_HIGH_RES_TO_SPLIT_DICT = PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS.dropna().split.to_dict()

ALL_HIGH_RES_CODES_WITH_SPLIT_BROAD_CODE = {high_res for high_res, split in _HIGH_RES_TO_SPLIT_DICT.items()}

ALL_HIGH_RES_CODES_WITH_ASSUMED_SPLIT_BROAD_CODE = set(map(_get_high_res_or_ultra_high_res,
                                                           PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS
                                                            .where(PARSED_DATAFRAME_WITH_HIGH_RES_TRANSFORMATIONS
                                                                   .source == 'assumed')
                                                            .dropna().split.to_dict().keys()))


def _get_possible_splits_for_high_res_code(high_res_code: str) -> Set[str]:
    return {split for high_res, split in _HIGH_RES_TO_SPLIT_DICT.items() if
            high_res.startswith(f'{high_res_code}:')}


def high_res_low_res_to_split_or_broad(high_res_code: str) -> Union[str, ParsingIssueDetail]:
    maybe_split_code = _HIGH_RES_TO_SPLIT_DICT.get(high_res_code)
    if maybe_split_code:
        return maybe_split_code
    else:
        possible_split_or_broad_codes = _get_possible_splits_for_high_res_code(high_res_code)
        if len(possible_split_or_broad_codes) == 0:
            return ParsingIssueDetail.UNPARSABLE_HLA_CODE

        maybe_split_or_broad_code = possible_split_or_broad_codes.pop()
        if len(possible_split_or_broad_codes) > 0:
            return ParsingIssueDetail.MULTIPLE_SPLITS_OR_BROADS_FOUND
        if maybe_split_or_broad_code is None:
            return ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES
        else:
            return maybe_split_or_broad_code


ALL_NON_ULTRA_HIGH_RES_CODES = {try_convert_ultra_high_res(high_res) for high_res in
                                ALL_HIGH_RES_CODES_WITH_SPLIT_BROAD_CODE}

HIGH_RES_TO_SPLIT_OR_BROAD = {high_res: high_res_low_res_to_split_or_broad(high_res) for high_res in
                              ALL_NON_ULTRA_HIGH_RES_CODES}

ALL_SEROLOGICAL_CODES_IN_TABLE = set(HIGH_RES_TO_SPLIT_OR_BROAD.values())

BROAD_CODES = {SPLIT_TO_BROAD.get(hla_code, hla_code) for hla_code in ALL_SEROLOGICAL_CODES_IN_TABLE}

SPLIT_CODES = ALL_SEROLOGICAL_CODES_IN_TABLE - set(SPLIT_TO_BROAD.values())

ALL_SPLIT_BROAD_CODES = ALL_SEROLOGICAL_CODES_IN_TABLE.union(BROAD_CODES)

IRRELEVANT_CODES = ['BW4', 'BW6']
