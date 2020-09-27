import { ListItem } from '@app/components/list-item/list-item.interface';

export interface PatientList {
  donors: Donor[];
  recipients: Recipient[];
}

export interface PatientPair extends ListItem {
  d: Donor;
  r: Recipient;
}

export interface Patient extends ListItem {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
}

export interface Recipient extends Patient {
  acceptable_blood_groups: string[];
  hla_antibodies: {
    antibodies_list: Antibody[];
    hla_codes_over_cutoff: string[];
  };
  recipient_requirements: RecipientRequirements;
}

export interface Donor extends Patient {
  donor_type: DonorType;
  related_recipient_db_id: number;
}

export interface PatientParameters {
  blood_group: string;
  hla_typing: {
    codes: string[];
  };
  country_code: string;
}

export interface RecipientRequirements {
  require_better_match_in_compatibility_index: boolean;
  require_better_match_in_compatibility_index_or_blood_group: boolean;
  require_compatible_blood_group: boolean;
}

export interface Antibody {
  code: string;
  cutoff: number;
  mfi: number;
}

export enum DonorType {
  DONOR = 'DONOR',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  ALTRUIST = 'ALTRUIST'
}

export const patientsLSKey = 'patients';

// recipient: [possible donors]
const compatibleBloodGroups: { [key: string]: string[]; } = {
  0: ['0'],
  A: ['0', 'A'],
  B: ['0', 'B'],
  AB: ['0', 'A', 'B', 'AB']
};

const antibodiesMultipliers: { [key: string]: number; } = {
  A: 1,
  B: 2,
  DR: 9
};

export { compatibleBloodGroups, antibodiesMultipliers };
