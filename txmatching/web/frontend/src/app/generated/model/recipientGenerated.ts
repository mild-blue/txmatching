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
import { RecipientRequirementsGenerated } from './recipientRequirementsGenerated';
import { PatientParametersGenerated } from './patientParametersGenerated';
import { HlaAntibodiesGenerated } from './hlaAntibodiesGenerated';


export interface RecipientGenerated { 
    acceptable_blood_groups?: Array<RecipientGeneratedAcceptableBloodGroupsEnum>;
    /**
     * Database id of the patient
     */
    db_id: number;
    hla_antibodies: HlaAntibodiesGenerated;
    /**
     * Medical id of the patient
     */
    medical_id: string;
    parameters: PatientParametersGenerated;
    previous_transplants?: number;
    recipient_cutoff?: number;
    recipient_requirements?: RecipientRequirementsGenerated;
    /**
     * Database id of the related donor
     */
    related_donor_db_id: number;
    waiting_since?: string;
}
export enum RecipientGeneratedAcceptableBloodGroupsEnum {
    A = 'A',
    B = 'B',
    Ab = 'AB',
    _0 = '0'
};



