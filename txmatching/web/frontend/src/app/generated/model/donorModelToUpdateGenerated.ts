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
import { DonorModelToUpdateAllOfGenerated } from './donorModelToUpdateAllOfGenerated';
import { SexEnumGenerated } from './sexEnumGenerated';
import { CountryCodeGenerated } from './countryCodeGenerated';
import { HlaTypingToUpdateGenerated } from './hlaTypingToUpdateGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';
import { PatientModelToUpdateGenerated } from './patientModelToUpdateGenerated';


export interface DonorModelToUpdateGenerated { 
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
     * Information, whether or not given donor shall be considered in exchange.
     */
    active?: boolean;
}

