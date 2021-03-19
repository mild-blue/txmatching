import { Patient } from '@app/model/Patient';
import { AntibodiesPerGroup, Antibody, AntibodyRaw } from '@app/model/Hla';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Recipient extends Patient {
  acceptable_blood_groups: BloodGroup[];
  cutoff?: number;
  waitingSince?: Date;
  previousTransplants?: number;
  hla_antibodies: {
    hla_antibodies_raw_list: AntibodyRaw[];
    hla_antibodies_per_groups: AntibodiesPerGroup[];
  };
  recipient_requirements?: RecipientRequirements;
  related_donor_db_id: number;
}

export interface RecipientRequirements {
  require_better_match_in_compatibility_index: boolean;
  require_better_match_in_compatibility_index_or_blood_group: boolean;
  require_compatible_blood_group: boolean;

  [key: string]: boolean;
}
