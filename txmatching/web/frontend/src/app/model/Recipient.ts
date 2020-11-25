import { Patient } from '@app/model/Patient';
import { Antibody, HlaGroupCodes } from '@app/model/Hla';

export interface Recipient extends Patient {
  acceptable_blood_groups: string[];
  hla_antibodies: {
    hla_antibodies_list: Antibody[];
    hla_codes_over_cutoff_per_group: HlaGroupCodes[];
  };
  recipient_requirements: RecipientRequirements;
  related_donor_db_id: number;
}

export interface RecipientRequirements {
  require_better_match_in_compatibility_index: boolean;
  require_better_match_in_compatibility_index_or_blood_group: boolean;
  require_compatible_blood_group: boolean;

  [key: string]: boolean;
}
