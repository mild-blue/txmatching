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


export interface ParsingIssueGenerated { 
    confirmed_at: string;
    confirmed_by: number;
    db_id: number;
    donor_id?: number;
    hla_code_or_group: string;
    message: string;
    parsing_issue_detail: string;
    recipient_id?: number;
    txm_event_id: number;
}

