import { Round } from '@app/model/Round';
import { NewListItem } from '@app/pages/abstract-list/abstract-list.component';

export interface CalculatedMatchings {
  calculatedMatchings: Matching[];
  configId: number;
  foundMatchingsCount?: number;
  showNotAllMatchingsFound: boolean;
}

export interface Matching extends NewListItem {
  orderId: number;
  score: number;
  countOfTransplants: number;
  rounds: Round[];
  countries: MatchingCountry[];
  hasCrossmatch: boolean;
}

export interface MatchingCountry {
  countryCode: string;
  donorCount: number;
  recipientCount: number;
}

export const matchingBatchSize = 10;
