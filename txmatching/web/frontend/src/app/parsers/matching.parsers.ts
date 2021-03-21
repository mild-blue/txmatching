import { CalculatedMatchingsGenerated, CountryGenerated, MatchingGenerated } from '../generated';
import { CalculatedMatchings, Matching, MatchingCountry, PatientList } from '../model';
import { parseRound } from './round.parsers';
import { NewListItem } from '@app/pages/abstract-list/abstract-list.component';

export const parseCalculatedMatchings = (data: CalculatedMatchingsGenerated, patients: PatientList): CalculatedMatchings => {
  return {
    calculatedMatchings: parseMatchings(data.calculated_matchings, patients),
    configId: data.config_id,
    foundMatchingsCount: data.found_matchings_count,
    showNotAllMatchingsFound: data.show_not_all_matchings_found
  };
};

export const parseMatchings = (data: MatchingGenerated[], patients: PatientList): Matching[] => {
  return data.map((matching, mKey) => {
    const listItem: NewListItem = {
      index: mKey + 1,
      isActive: mKey === 0
      // itemComponent: MatchingItemComponent,
      // detailComponent: MatchingDetailComponent
    };
    return parseMatching(matching, patients, listItem);
  });
};

export const parseMatching = (data: MatchingGenerated, patients: PatientList, listItem: NewListItem): Matching => {
  const rounds = data.rounds.map((round, rKey) =>
    parseRound(round, patients, listItem.index, rKey + 1)
  );
  return {
    ...listItem,
    orderId: data.order_id,
    score: data.score,
    countOfTransplants: data.count_of_transplants,
    rounds,
    countries: data.countries.map(parseMatchingCountry),
    hasCrossmatch: rounds.some(round => round.hasCrossmatch)
  };
};

export const parseMatchingCountry = (data: CountryGenerated): MatchingCountry => {
  return {
    countryCode: data.country_code,
    donorCount: data.donor_count,
    recipientCount: data.recipient_count
  };
};
