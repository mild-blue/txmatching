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
import { HlaCodeGenerated } from './hlaCodeGenerated';


export interface CrossmatchSummaryGenerated { 
    hla_code: HlaCodeGenerated;
    issues?: Array<CrossmatchSummaryGeneratedIssuesEnum>;
    match_type: CrossmatchSummaryGeneratedMatchTypeEnum;
    mfi?: number;
}
export enum CrossmatchSummaryGeneratedIssuesEnum {
    ThereIsMostLikelyNoCrossmatchButThereIsASmallChanceThatACrossmatchCouldOccurThereforeThisCaseRequiresFurtherInvestigationInSummaryWeSendSplitResolutionOfAnInfrequentCodeWithTheHighestMfiValueAmongAntibodiesThatHaveRarePositiveCrossmatch = 'There is most likely no crossmatch, but there is a small chance that a crossmatch could occur. Therefore, this case requires further investigation.In summary we send SPLIT resolution of an infrequent code with the highest MFI value among antibodies that have rare positive crossmatch.',
    AntibodiesAgainstThisHlaTypeMightNotBeDsaForMoreSeeDetailedSection = 'Antibodies against this HLA Type might not be DSA, for more see detailed section.',
    ThereAreNoFrequentAntibodiesCrossmatchedAgainstThisHlaTypeTheHlaCodeInSummaryCorrespondsToAnAntibodyWithMfiBelowCutoffAndIsThereforeNotDisplayedInTheListOfMatchedAntibodies = 'There are no frequent antibodies crossmatched against this HLA type, the HLA code in summary corresponds to an antibody with mfi below cutoff and is therefore not displayed in the list of matched antibodies.',
    NoMatchingAntibodyWasFoundAgainstThisHlaTypeHlaCodeDisplayedInSummaryTakenFromTheHlaType = 'No matching antibody was found against this HLA type, HLA code displayed in summary taken from the HLA type.'
};
export enum CrossmatchSummaryGeneratedMatchTypeEnum {
    Split = 'SPLIT',
    Broad = 'BROAD',
    HighRes = 'HIGH_RES',
    None = 'NONE',
    Undecidable = 'UNDECIDABLE',
    HighResWithSplit = 'HIGH_RES_WITH_SPLIT',
    HighResWithBroad = 'HIGH_RES_WITH_BROAD',
    Theoretical = 'THEORETICAL'
};



