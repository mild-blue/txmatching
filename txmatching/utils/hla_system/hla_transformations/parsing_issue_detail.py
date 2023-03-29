from enum import Enum

from txmatching.utils.constants import \
    SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES


class ParsingIssueDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected.'
    HIGH_RES_WITHOUT_SPLIT = 'High res can be converted to broad resolution but split resolution is unknown'
    HIGH_RES_WITH_LETTER = 'High res code has letter in the end. Such codes are not converted to split and broad.'
    HIGH_RES_WITH_ASSUMED_SPLIT_CODE = 'The information about the serological equivalent of the allele is only assumed' \
                                       ' in our datasource so the conversion is not 100% reliable. ' \
                                       'Please check that the conversion is correct.'
    CREATED_THEORETICAL_ANTIBODY = 'Theoretical antibody was created, because double antibody had mixed MFI values ' \
                                   'for both chains.'

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
    ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES = 'All antibodies are in high resolution, and all of them are above' \
                                              ' cutoff. This is fine and antibodies will be processed properly, but ' \
                                              ' it is better to all antibodies the patient was tested for to improve' \
                                              ' crossmatch estimation.'
    INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES = \
        f'All antibodies are in high resolution, some of them below cutoff and less then ' \
        f'{SUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES} were provided. This is fine and antibodies' \
        ' will be processed properly, but we are assuming that not all antibodies the patient was tested for were ' \
        'sent. It is better to send all to improve crossmatch estimation.'

    # not in a result of parse_hla_raw_code_with_details method
    MULTIPLE_CUTOFFS_PER_GROUP = 'There were multiple cutoff values for antibodies in this group. ' \
                                    'This means inconsistency that is not allowed.'
    DUPLICATE_ANTIBODY_SINGLE_CHAIN = 'There were multiple instances of the same antibody with a single chain. ' \
                                      'This is not allowed, please ensure that this antibody occurs only once in this format.'

    MFI_PROBLEM = 'There is a problem with MFI.'  # This string value is not used but we have it here as a fallback
    OTHER_PROBLEM = 'Some problem occurred when processing this code.'


OK_PROCESSING_RESULTS = {
    ParsingIssueDetail.SUCCESSFULLY_PARSED,
    ParsingIssueDetail.HIGH_RES_WITHOUT_SPLIT,
    ParsingIssueDetail.HIGH_RES_WITH_LETTER
}

WARNING_PROCESSING_RESULTS = {
    ParsingIssueDetail.IRRELEVANT_CODE,
    ParsingIssueDetail.MULTIPLE_SPLITS_OR_BROADS_FOUND,
    ParsingIssueDetail.MFI_PROBLEM,
    ParsingIssueDetail.ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES,
    ParsingIssueDetail.INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES,
    ParsingIssueDetail.HIGH_RES_WITH_ASSUMED_SPLIT_CODE,
    ParsingIssueDetail.CREATED_THEORETICAL_ANTIBODY
}

ERROR_PROCESSING_RESULTS = {
    ParsingIssueDetail.MULTIPLE_CUTOFFS_PER_GROUP,
    ParsingIssueDetail.OTHER_PROBLEM,
    ParsingIssueDetail.UNEXPECTED_SPLIT_RES_CODE,
    ParsingIssueDetail.UNKNOWN_TRANSFORMATION_FROM_HIGH_RES,
    ParsingIssueDetail.UNPARSABLE_HLA_CODE,
    ParsingIssueDetail.MORE_THAN_TWO_HLA_CODES_PER_GROUP,
    ParsingIssueDetail.BASIC_HLA_GROUP_IS_EMPTY,
    ParsingIssueDetail.DUPLICATE_ANTIBODY_SINGLE_CHAIN
}
