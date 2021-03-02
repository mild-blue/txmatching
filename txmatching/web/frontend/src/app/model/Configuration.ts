import { ConfigurationGeneratedSolverConstructorNameEnum, CountryCodeGenerated } from '@app/generated';

export interface Configuration {
  use_split_resolution: boolean;
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
  max_matchings_to_show_to_viewer: number;
  max_number_of_matchings: number;

  // complex FE
  manual_donor_recipient_scores: DonorRecipientScore[];
  required_patient_db_ids: number[];
  forbidden_country_combinations: CountryCombination[];

  solver_constructor_name: ConfigurationGeneratedSolverConstructorNameEnum;

  // Parameters that should not be modified in FE
  max_cycles_in_all_solutions_solver: number;
  max_matchings_in_all_solutions_solver: number;
  max_matchings_in_ilp_solver: number;

  [key: string]: boolean | string | number | number[] | CountryCombination[] | DonorRecipientScore[];
}

export interface AppConfiguration extends Configuration {
  scorer_constructor_name: string;
}

export interface DonorRecipientScore {
  donor_db_id: number;
  recipient_db_id: number;
  score: number;
}

export interface CountryCombination {
  donor_country: CountryCodeGenerated;
  recipient_country: CountryCodeGenerated;
}
