export interface Configuration {
  enforce_compatible_blood_group: boolean;
  require_new_donor_having_better_match_in_compatibility_index: boolean;
  require_new_donor_having_better_match_in_compatibility_index_or_blood_group: boolean;
  use_binary_scoring: boolean;
  minimum_total_score: number;
  max_cycle_length: number;
  max_sequence_length: number;
  max_number_of_distinct_countries_in_round: number;
  manual_donor_recipient_scores_dto: string;

  [key: string]: boolean | string | number | number[];
}

export interface AppConfiguration extends Configuration {
  scorer_constructor_name: string;
  solver_constructor_name: string;
  maximum_total_score: number;
  required_patient_db_ids: number[];
}

// export type configurationType = {
//   [key: string]: boolean | string
// }
