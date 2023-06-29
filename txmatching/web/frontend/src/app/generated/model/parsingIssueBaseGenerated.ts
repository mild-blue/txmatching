/**
 * API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


export interface ParsingIssueBaseGenerated { 
    hla_code_or_group: string;
    message: string;
    parsing_issue_detail: ParsingIssueBaseGeneratedParsingIssueDetailEnum;
}
export enum ParsingIssueBaseGeneratedParsingIssueDetailEnum {
    SuccessfullyParsed = 'SUCCESSFULLY_PARSED',
    HighResWithoutSplit = 'HIGH_RES_WITHOUT_SPLIT',
    HighResWithLetter = 'HIGH_RES_WITH_LETTER',
    HighResWithAssumedSplitCode = 'HIGH_RES_WITH_ASSUMED_SPLIT_CODE',
    CreatedTheoreticalAntibody = 'CREATED_THEORETICAL_ANTIBODY',
    MultipleSplitsOrBroadsFound = 'MULTIPLE_SPLITS_OR_BROADS_FOUND',
    IrrelevantCode = 'IRRELEVANT_CODE',
    UnexpectedSplitResCode = 'UNEXPECTED_SPLIT_RES_CODE',
    UnknownTransformationFromHighRes = 'UNKNOWN_TRANSFORMATION_FROM_HIGH_RES',
    UnparsableHlaCode = 'UNPARSABLE_HLA_CODE',
    MoreThanTwoHlaCodesPerGroup = 'MORE_THAN_TWO_HLA_CODES_PER_GROUP',
    BasicHlaGroupIsEmpty = 'BASIC_HLA_GROUP_IS_EMPTY',
    AllAntibodiesArePositiveInHighRes = 'ALL_ANTIBODIES_ARE_POSITIVE_IN_HIGH_RES',
    InsufficientNumberOfAntibodiesInHighRes = 'INSUFFICIENT_NUMBER_OF_ANTIBODIES_IN_HIGH_RES',
    MultipleCutoffsPerGroup = 'MULTIPLE_CUTOFFS_PER_GROUP',
    DuplicateAntibodySingleChain = 'DUPLICATE_ANTIBODY_SINGLE_CHAIN',
    MfiProblem = 'MFI_PROBLEM',
    OtherProblem = 'OTHER_PROBLEM'
};



