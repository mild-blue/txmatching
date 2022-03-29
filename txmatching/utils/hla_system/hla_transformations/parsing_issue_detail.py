from enum import Enum


class ParsingIssueDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected.'
    HIGH_RES_WITHOUT_SPLIT = 'High res can be converted to broad resolution but split resolution is unknown'
    HIGH_RES_WITH_LETTER = 'High res code has letter in the end. Such codes are not converted to split and broad.'

    # returning no value (hla code)
    MULTIPLE_SPLITS_OR_BROADS_FOUND = 'Multiple splits or broad were found, unable to choose the right one.' \
                                      ' Immunologists should be contacted.'
    IRRELEVANT_CODE = 'This type of code is not relevant for further matching.'
    UNEXPECTED_SPLIT_RES_CODE = 'Unknown HLA code, seems to be in split resolution.'
    UNKNOWN_TRANSFORMATION_FROM_HIGH_RES = 'Unable to transform high resolution HLA code. Its transformation to ' \
                                           'split or broad code is unknown. Immunologists should be contacted.'
    UNPARSABLE_HLA_CODE = 'Completely Unexpected HLA code.'

    # returning no value (hla group)
    MORE_THAN_TWO_HLA_CODES_PER_GROUP = 'There can not be more than 2 antigens per group.'
    BASIC_HLA_GROUP_IS_EMPTY = 'This HLA group should contain at least one antigen.'
    INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES = 'There should be at least 20 antibodies in high resolution.'
    ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES = 'There are only positive antibodies in high resolution.'

    # not in a result of parse_hla_raw_code_with_details method
    MULTIPLE_CUTOFFS_PER_ANTIBODY = 'There were multiple cutoff values for antibody. ' \
                                    'This means inconsistency that is not allowed.'

    MFI_PROBLEM = 'There is a problem with MFI.'  # This string value is not used but we have it here as a fallback
    OTHER_PROBLEM = 'Some problem occurred when processing this code.'


OK_PROCESSING_RESULTS = {
    ParsingIssueDetail.SUCCESSFULLY_PARSED,
    ParsingIssueDetail.HIGH_RES_WITHOUT_SPLIT,
    ParsingIssueDetail.HIGH_RES_WITH_LETTER
}

WARNING_PROCESSING_RESULTS = {
    ParsingIssueDetail.MULTIPLE_SPLITS_OR_BROADS_FOUND,
    ParsingIssueDetail.IRRELEVANT_CODE,
    ParsingIssueDetail.UNEXPECTED_SPLIT_RES_CODE,
    ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES,
    ParsingIssueDetail.UNPARSABLE_HLA_CODE,
    ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP,
    ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
    ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
    ParsingIssueDetail.ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES
}

ERROR_PROCESSING_RESULTS = {
    ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_ANTIBODY,
    ParsingIssueDetail.MFI_PROBLEM,
    ParsingIssueDetail.OTHER_PROBLEM,
}
