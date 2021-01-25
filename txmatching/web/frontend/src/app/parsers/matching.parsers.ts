import { CalculatedMatchingsGenerated, CountryGenerated, MatchingGenerated } from '../generated';
import { CalculatedMatchings, Matching, MatchingCountry, PatientList } from '../model';
import { ListItem } from '../components/list-item/list-item.interface';
import { parseRound } from './round.parsers';
import { MatchingItemComponent } from '@app/components/matching-item/matching-item.component';
import { MatchingDetailComponent } from '@app/components/matching-detail/matching-detail.component';

export const parseCalculatedMatchings = (data: CalculatedMatchingsGenerated, patients: PatientList): CalculatedMatchings => {
  return {
    calculated_matchings: parseMatchings(data.calculated_matchings, patients),
    found_matchings_count: data.found_matchings_count,
    show_not_all_matchings_found: data.show_not_all_matchings_found
  };
};

export const parseMatchings = (data: MatchingGenerated[], patients: PatientList): Matching[] => {
  return data.map((matching, mKey) => {
    const listItem: ListItem = {
      index: mKey + 1,
      isActive: mKey === 0,
      itemComponent: MatchingItemComponent,
      detailComponent: MatchingDetailComponent
    };
    return parseMatching(matching, patients, listItem);
  });
};

export const parseMatching = (data: MatchingGenerated, patients: PatientList, listItem: ListItem): Matching => {
  return {
    ...listItem,
    order_id: data.order_id,
    score: data.score,
    count_of_transplants: data.count_of_transplants,
    rounds: data.rounds.map((round, rKey) =>
      parseRound(round, patients, listItem.index, rKey + 1)
    ),
    countries: data.countries.map(parseMatchingCountry)
  };
};

export const parseMatchingCountry = (data: CountryGenerated): MatchingCountry => {
  return {
    country_code: data.country_code,
    donor_count: data.donor_count,
    recipient_count: data.recipient_count
  };
};
