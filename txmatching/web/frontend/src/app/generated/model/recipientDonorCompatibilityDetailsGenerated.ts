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
import { DetailedScoreForGroupGenerated } from './detailedScoreForGroupGenerated';


export interface RecipientDonorCompatibilityDetailsGenerated { 
    /**
     * Indicator whether donor and recipient have compatible blood groups
     */
    compatible_blood: boolean;
    /**
     * Contains details for compatibility index for each HLA Group compatibility index is calculated for.
     */
    detailed_score: Array<DetailedScoreForGroupGenerated>;
    /**
     * Database id of the donor
     */
    donor_db_id: number;
    /**
     * Maximum transplant score
     */
    max_score: number;
    /**
     * Database id of the recipient
     */
    recipient_db_id: number;
    /**
     * Compatibility score if donor and recipient
     */
    score: number;
}

