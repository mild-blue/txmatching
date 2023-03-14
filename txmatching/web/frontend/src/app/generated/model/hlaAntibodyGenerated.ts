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
import { HLAAntibodyTypeGenerated } from './hLAAntibodyTypeGenerated';
import { HlaCodeGenerated } from './hlaCodeGenerated';


export interface HlaAntibodyGenerated {
    code: HlaCodeGenerated;
    cutoff: number;
    mfi: number;
    raw_code: string;
    second_code?: HlaCodeGenerated;
    second_raw_code?: string;
    type: HLAAntibodyTypeGenerated;
}

