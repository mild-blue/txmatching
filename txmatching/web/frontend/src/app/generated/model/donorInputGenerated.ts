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


export interface DonorInputGenerated { 
    blood_group: DonorInputGeneratedBloodGroupEnum;
    donor_type: DonorInputGeneratedDonorTypeEnum;
    /**
     * Height of the patient in centimeters.
     */
    height?: number;
    /**
     * HLA typing of the patient. Use high resolution if available.
     */
    hla_typing: Array<string>;
    /**
     * Medical ID of the patient. This ID is unique thorough the system and can be used for the identification of a specific patient in your system. Typically, this is the patient ID used in your internal system.
     */
    medical_id: string;
    /**
     * Medical ID of the related recipient, empty for bridging and non-directed donors.
     */
    related_recipient_medical_id?: string;
    /**
     * Sex of the patient.
     */
    sex?: DonorInputGeneratedSexEnum;
    /**
     * Weight of the patient in kilograms.
     */
    weight?: number;
    /**
     * Year of birth of the patient.
     */
    year_of_birth?: number;
}
export enum DonorInputGeneratedBloodGroupEnum {
    A = 'A',
    B = 'B',
    Ab = 'AB',
    _0 = '0'
};
export enum DonorInputGeneratedDonorTypeEnum {
    Donor = 'DONOR',
    BridgingDonor = 'BRIDGING_DONOR',
    NonDirected = 'NON_DIRECTED'
};
export enum DonorInputGeneratedSexEnum {
    M = 'M',
    F = 'F'
};



