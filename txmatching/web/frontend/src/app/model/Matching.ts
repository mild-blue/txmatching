import { ListItem } from '@app/components/list-item/list-item.interface';
import { Round } from '@app/model/Round';

export interface Matching extends ListItem {
  order_id: number;
  score: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface MatchingCountry {
  country_code: string;
  donor_count: number;
  recipient_count: number;
}

export const matchingBatchSize = 10;
