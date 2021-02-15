import { Antibody } from '@app/model';

export interface DonorModelPairIn {
  country_code: string;
  donor: DonorInput;
  recipient?: RecipientInput;
}

export interface DonorInput {
  blood_group: string;
  donor_type: string;
  height?: number;
  hla_typing: string[];
  medical_id: string;
  related_recipient_medical_id?: string;
  sex?: string;
  weight?: number;
  year_of_birth?: number;
}

export interface RecipientInput {
  acceptable_blood_groups?: string[];
  blood_group: string;
  height?: number;
  hla_antibodies: Antibody[];
  hla_typing: string[];
  medical_id: string;
  previous_transplants?: number;
  sex?: string;
  waiting_since?: string;
  weight?: number;
  year_of_birth?: number;
}
