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
import { HLAAntibodyInGenerated } from './hLAAntibodyInGenerated';
import { SexEnumGenerated } from './sexEnumGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';


export interface RecipientInputGenerated { 
    /**
     * Acceptable blood groups for the patient. Leave empty to use compatible blood groups.
     */
    acceptable_blood_groups?: Array<BloodGroupEnumGenerated>;
    blood_group: BloodGroupEnumGenerated;
    /**
     * Height of the patient in centimeters.
     */
    height?: number;
    /**
     * Detected HLA antibodies of the patient. Use high resolution if available. If high resolution is provided it is assumed that all tested antibodies were provided. If not it is assumed that either all or just positive ones were.
     */
    hla_antibodies: Array<HLAAntibodyInGenerated>;
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
     * Number of previous kidney transplants.
     */
    previous_transplants?: number;
    sex?: SexEnumGenerated;
    /**
     * Date since when the patient has been on waiting list. Use format YYYY-MM-DD.
     */
    waiting_since?: string;
    /**
     * Weight of the patient in kilograms.
     */
    weight?: number;
    /**
     * Year of birth of the patient.
     */
    year_of_birth?: number;
}

