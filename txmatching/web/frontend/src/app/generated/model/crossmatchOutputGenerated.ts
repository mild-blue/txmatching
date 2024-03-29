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
import { ParsingIssueBaseGenerated } from './parsingIssueBaseGenerated';
import { AntibodyMatchForHLATypeGenerated } from './antibodyMatchForHLATypeGenerated';


export interface CrossmatchOutputGenerated { 
    datetime?: string;
    donor_code?: string;
    donor_sample_id?: string;
    hla_to_antibody: Array<AntibodyMatchForHLATypeGenerated>;
    is_positive_crossmatch: boolean;
    parsing_issues: Array<ParsingIssueBaseGenerated>;
    recipient_id?: string;
    recipient_sample_id?: string;
}

