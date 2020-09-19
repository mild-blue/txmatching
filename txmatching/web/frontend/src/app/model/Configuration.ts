export interface Configuration {
  allow_low_high_res_incompatible: boolean;
  require_compatible_blood_group: boolean;
  require_better_match_in_compatibility_index: boolean;
  require_better_match_in_compatibility_index_or_blood_group: boolean;
  use_binary_scoring: boolean;

  blood_group_compatibility_bonus: number;
  minimum_total_score: number;
  maximum_total_score: number;
  max_cycle_length: number;
  max_sequence_length: number;
  max_number_of_distinct_countries_in_round: number;

  // No need?
  max_matchings_to_show_to_viewer: number;

  // complex FE
  manual_donor_recipient_scores: DonorRecipientScore[];
  required_patient_db_ids: number[];
  forbidden_country_combinations: CountryCombination[];

  [key: string]: boolean | string | number | number[] | CountryCombination[] | DonorRecipientScore[];
}

export interface AppConfiguration extends Configuration {
  scorer_constructor_name: string;
  solver_constructor_name: string;
}

export interface DonorRecipientScore {
  donor?: number;
  recipient?: number;
  score?: number;
}

export interface CountryCombination {
  donor_country: string;
  recipient_country: string;
}
