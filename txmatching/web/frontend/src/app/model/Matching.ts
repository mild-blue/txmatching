import { ListItem } from '@app/components/list-item/list-item.interface';

export interface Matching extends ListItem {
  score: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface Round {
  transplants: Transplant[];
}

export interface Transplant {
  score: number;
  compatible_blood: boolean;
  donor: string;
  recipient: string;
}

export interface MatchingCountry {
  country_code: string;
  donor_count: number;
  recipient_count: number;
}

export const matchingBatchSize = 10;
