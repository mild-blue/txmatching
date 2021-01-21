import { CalculatedMatchingsGenerated, CountryGenerated, MatchingGenerated } from '../generated';
import { CalculatedMatchings, Matching, MatchingCountry, PatientList } from '../model';
import { DEFAULT_LIST_ITEM } from '../components/list-item/list-item.interface';
import { parseRound } from './round.parsers';

export const parseCalculatedMatchings = (data: CalculatedMatchingsGenerated, patients: PatientList): CalculatedMatchings => {
  return {
    calculated_matchings: data.calculated_matchings.map(_ => parseMatching(_, patients)),
    found_matchings_count: data.found_matchings_count,
    show_not_all_matchings_found: data.show_not_all_matchings_found
  };
};

export const parseMatching = (data: MatchingGenerated, patients: PatientList): Matching => {
  return {
    // TODO: create proper ListItem here
    ...DEFAULT_LIST_ITEM,
    order_id: data.order_id,
    score: data.score,
    count_of_transplants: data.count_of_transplants,
    rounds: data.rounds.map(_ => parseRound(_, patients)),
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
