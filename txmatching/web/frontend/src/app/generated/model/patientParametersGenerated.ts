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
import { CountryCodeGenerated } from './countryCodeGenerated';
import { HlaTypingGenerated } from './hlaTypingGenerated';
import { BloodGroupEnumGenerated } from './bloodGroupEnumGenerated';


export interface PatientParametersGenerated { 
    blood_group: BloodGroupEnumGenerated;
    country_code: CountryCodeGenerated;
    height?: number;
    hla_typing?: HlaTypingGenerated;
    note: string;
    sex?: SexEnumGenerated;
    weight?: number;
    year_of_birth?: number;
}

