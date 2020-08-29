export interface Configuration {
  scorer_constructor_name: string;
  solver_constructor_name: string;
  enforce_compatible_blood_group: boolean;
  minimum_total_score: number;
  maximum_total_score: number;
  require_new_donor_having_better_match_in_compatibility_index: boolean;
  require_new_donor_having_better_match_in_compatibility_index_or_blood_group: boolean;
  use_binary_scoring: boolean;
  max_cycle_length: number;
  max_sequence_length: number;
  max_number_of_distinct_countries_in_round: number;
  required_patient_db_ids: number[];
  manual_donor_recipient_scores_dto: string;
}
