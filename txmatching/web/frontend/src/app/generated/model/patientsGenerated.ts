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
import { DonorGenerated } from './donorGenerated';
import { RecipientGenerated } from './recipientGenerated';


export interface PatientsGenerated {
    donors?: Array<DonorGenerated>;
    recipients?: Array<RecipientGenerated>;
}
