import { ListItem } from '@app/components/list-item/list-item.interface';
import { Round } from '@app/model/Round';

export interface CalculatedMatchings {
  calculated_matchings: Matching[];
  calculation_id: number;
  found_matchings_count?: number;
  show_not_all_matchings_found: boolean;
}

export interface Matching extends ListItem {
  order_id: number;
  score: number;
  count_of_transplants: number;
  rounds: Round[];
  countries: MatchingCountry[];
  hasCrossmatch: boolean;
}

export interface MatchingCountry {
  country_code: string;
  donor_count: number;
  recipient_count: number;
}

export const matchingBatchSize = 10;
