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
import { RecipientInputGenerated } from './recipientInputGenerated';
import { CountryCodeGenerated } from './countryCodeGenerated';
import { DonorInputGenerated } from './donorInputGenerated';


export interface DonorModelPairInGenerated {
    country_code?: CountryCodeGenerated;
    donor: DonorInputGenerated;
    recipient?: RecipientInputGenerated;
}
    country_code?: DonorModelPairInGeneratedCountryCodeEnum;
    donor: DonorInputGenerated;
    recipient?: RecipientInputGenerated;
}
export enum DonorModelPairInGeneratedCountryCodeEnum {
    Cze = 'CZE',
    Isr = 'ISR',
    Aut = 'AUT',
    Can = 'CAN',
    Ind = 'IND'
};



// TODOO
