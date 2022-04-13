import { ListItem } from '@app/components/list-item/list-item.interface';
import { Round } from '@app/model/Round';

export interface CalculatedMatchings {
  calculatedMatchings: Matching[];
  configId: number;
  foundMatchingsCount?: number;
  showNotAllMatchingsFound: boolean;
}

export interface Matching extends ListItem {
  orderId: number;
  score: number;
  countOfTransplants: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface MatchingCountry {
  countryCode: string;
  donorCount: number;
  recipientCount: number;
}

export const matchingBatchSize = 10;
