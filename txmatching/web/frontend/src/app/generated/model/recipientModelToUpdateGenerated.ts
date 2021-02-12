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
import { RecipientModelToUpdateAllOfGenerated } from './recipientModelToUpdateAllOfGenerated';
import { RecipientRequirementsGenerated } from './recipientRequirementsGenerated';
import { SexEnumGenerated } from './sexEnumGenerated';
import { CountryCodeGenerated } from './countryCodeGenerated';
import { HlaAntibodiesToUpdateGenerated } from './hlaAntibodiesToUpdateGenerated';
import { HlaTypingToUpdateGenerated } from './hlaTypingToUpdateGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';
import { PatientModelToUpdateGenerated } from './patientModelToUpdateGenerated';


export interface RecipientModelToUpdateGenerated { 
    blood_group?: BloodGroupEnumGenerated;
    country_code?: CountryCodeGenerated;
    /**
     * Database id of the patient
     */
    db_id: number;
    height?: number;
    /**
     * Provide full list of all the HLA types of the patient, not just the change set
     */
    hla_typing?: HlaTypingToUpdateGenerated;
    sex?: SexEnumGenerated;
    weight?: number;
    year_of_birth?: number;
    /**
     * Provide full list of all the acceptable blood groups of the patient, not just the change set
     */
    acceptable_blood_groups?: Array<BloodGroupEnumGenerated>;
    cutoff?: number;
    /**
     * Provide full list of all the HLA antibodies of the patient, not just the change set
     */
    hla_antibodies?: HlaAntibodiesToUpdateGenerated;
    /**
     * Provide the whole recipients requirements object, it will be overwritten
     */
    recipient_requirements?: RecipientRequirementsGenerated;
}

