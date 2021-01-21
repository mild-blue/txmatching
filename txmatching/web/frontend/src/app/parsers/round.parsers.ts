import { CalculatedMatchingsGenerated, RoundGenerated } from '../generated';
import { DonorType, PatientList, Round } from '../model';
import { parseTransplant } from './transplant.parsers';

export const parseRound = (data: RoundGenerated, patients: PatientList): Round => {
  return {
    // TODO: set proper index and donorType here
    index: '',
    donorType: DonorType.DONOR,
    transplants: data.transplants?.map(_ => parseTransplant(_, patients)) ?? []
  };
};
