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
import { ForbiddenCountryCombinationGenerated } from './forbiddenCountryCombinationGenerated';
import { ManualRecipientDonorScoreGenerated } from './manualRecipientDonorScoreGenerated';


export interface ConfigurationGenerated { 
    blood_group_compatibility_bonus: number;
    forbidden_country_combinations: Array<ForbiddenCountryCombinationGenerated>;
    manual_donor_recipient_scores: Array<ManualRecipientDonorScoreGenerated>;
    max_cycle_length: number;
    max_cycles_in_all_solutions_solver: number;
    max_debt_for_country: number;
    max_matchings_in_all_solutions_solver: number;
    max_matchings_in_ilp_solver: number;
    max_matchings_to_show_to_viewer: number;
    max_number_of_distinct_countries_in_round: number;
    max_number_of_dynamic_constrains_ilp_solver: number;
    max_number_of_matchings: number;
    max_sequence_length: number;
    maximum_total_score: number;
    minimum_total_score: number;
    require_better_match_in_compatibility_index: boolean;
    require_better_match_in_compatibility_index_or_blood_group: boolean;
    require_compatible_blood_group: boolean;
    required_patient_db_ids: Array<number>;
    scorer_constructor_name: string;
    solver_constructor_name: ConfigurationGeneratedSolverConstructorNameEnum;
    use_binary_scoring: boolean;
    use_high_res_resolution: boolean;
}
export enum ConfigurationGeneratedSolverConstructorNameEnum {
    AllSolutionsSolver = 'AllSolutionsSolver',
    IlpSolver = 'ILPSolver'
};



