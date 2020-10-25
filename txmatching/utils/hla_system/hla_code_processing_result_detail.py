from enum import Enum


class HlaCodeProcessingResultDetail(str, Enum):
    # still returning value
    SUCCESSFULLY_PARSED = 'Code successfully parsed without anything unexpected.'
    UNEXPECTED_SPLIT_RES_CODE = 'Unknown HLA code, seems to be in split resolution.'

    # returning no value
    MULTIPLE_SPLITS_FOUND = 'Multiple splits were found, unable to choose the right one.' \
                            ' Immunologists should be contacted.'
    UNKNOWN_TRANSFORMATION_TO_SPLIT = 'Unable to transform high resolution HLA code. Its transformation to split' \
                                      ' code is unknown. Immunologists should be contacted.'
    UNPARSABLE_HLA_CODE = 'Completely Unexpected HLA code.'
