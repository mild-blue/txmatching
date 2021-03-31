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
import { SexEnumGenerated } from './sexEnumGenerated';
import { DonorTypeGenerated } from './donorTypeGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';


export interface DonorInputGenerated { 
    blood_group: BloodGroupEnumGenerated;
    donor_type: DonorTypeGenerated;
    /**
     * Height of the patient in centimeters.
     */
    height?: number;
    /**
     * HLA typing of the patient. Use high resolution if available.
     */
    hla_typing: Array<string>;
    /**
     * Custom medical ID that will not be shown in UI, but will be stored and can be seen in patient xlsx export.
     */
    internal_medical_id?: string;
    /**
     * Medical ID of the patient. This ID is unique thorough the system and can be used for the identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.
     */
    medical_id: string;
    note?: string;
    /**
     * Medical ID of the related recipient, empty for bridging and non-directed donors.
     */
    related_recipient_medical_id?: string;
    sex?: SexEnumGenerated;
    /**
     * Weight of the patient in kilograms.
     */
    weight?: number;
    /**
     * Year of birth of the patient.
     */
    year_of_birth?: number;
}

