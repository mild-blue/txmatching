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
import { ParsingIssuePublicGenerated } from './parsingIssuePublicGenerated';


export interface PatientUploadSuccessResponseGenerated { 
    /**
     * Number of donors successfully loaded into the application.
     */
    donors_uploaded: number;
    /**
     * Errors and warnings that occurred in HLA codes parsing
     */
    parsing_issues: Array<ParsingIssuePublicGenerated>;
    /**
     * Number of recipients successfully loaded into the application.
     */
    recipients_uploaded: number;
}

