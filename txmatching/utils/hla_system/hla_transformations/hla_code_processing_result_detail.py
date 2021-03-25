from enum import Enum


class HlaCodeProcessingResultDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected.'
    HIGH_RES_WITHOUT_SPLIT = 'High res can be converted to broad resolution but split resolution is unknown'
    HIGH_RES_WITH_LETTER = 'High res code has letter in the end. Such codes are not converted to split and broad.'

    # returning no value
    MULTIPLE_SPLITS_OR_BROADS_FOUND = 'Multiple splits or broad were found, unable to choose the right one.' \
                                      ' Immunologists should be contacted.'
    UNEXPECTED_SPLIT_RES_CODE = 'Unknown HLA code, seems to be in split resolution.'
    UNKNOWN_TRANSFORMATION_FROM_HIGH_RES = 'Unable to transform high resolution HLA code. Its transformation to ' \
                                           'split or broad code is unknown. Immunologists should be contacted.'
    UNPARSABLE_HLA_CODE = 'Completely Unexpected HLA code.'

    # not in a result of parse_hla_raw_code_with_details method
    MULTIPLE_CUTOFFS_PER_ANTIBODY = 'There were multiple cutoff values for antibody. ' \
                                    'This means inconsistency that is not allowed.'
