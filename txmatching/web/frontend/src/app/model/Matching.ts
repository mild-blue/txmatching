import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientPair } from '@app/model/PatientPair';
import { DonorType } from '@app/model/Donor';

export interface Matching extends ListItem {
  order_id: number;
  score: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface Round {
  transplants: Transplant[];
  donorType: DonorType;
  index?: string;
}

export interface Transplant extends PatientPair {
  score?: number;
  compatible_blood?: boolean;
  donor?: string;
  recipient?: string;
}

export interface MatchingCountry {
  country_code: string;
  donor_count: number;
  recipient_count: number;
}

export const matchingBatchSize = 10;
