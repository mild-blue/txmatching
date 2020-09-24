export interface Matching {
  score: number;
  rounds: Round[];
  countries: MatchingCountry[];
}

export interface MatchingView extends Matching {
  index: number;
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
export const defaultViewerMatchingCount = 10;
