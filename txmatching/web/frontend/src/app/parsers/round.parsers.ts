import { CalculatedMatchingsGenerated, RoundGenerated } from '../generated';
import { DonorType, PatientList, Round, Transplant } from '../model';
import { parseTransplant } from './transplant.parsers';

export const parseRound = (data: RoundGenerated, patients: PatientList, mIndex: number, rIndex: number): Round => {
  const transplants = data.transplants?.map((t, tKey) =>
    parseTransplant(t, patients, +`${mIndex}${rIndex}${tKey + 1}`)
  ) ?? []
  const donorType = _getRoundDonorType(transplants);
  const index = _getRoundIndex(donorType, rIndex);

  return {
    index,
    donorType,
    transplants
  };
};

const _getRoundDonorType = (transplants: Transplant[]): DonorType => {
  if (!transplants.length) {
    return DonorType.DONOR;
  }

  const firstTransplant = transplants[0];
  const donor = firstTransplant.d;

  if (donor) {
    return donor.donor_type;
  }

  return DonorType.DONOR;
};

const _getRoundIndex = (donorType: DonorType, order: number): string => {
  const roundIndex = `${order}`;

  if (donorType === DonorType.BRIDGING_DONOR.valueOf()) {
    return `${roundIndex}B`;
  }
  if (donorType === DonorType.NON_DIRECTED.valueOf()) {
    return `${roundIndex}N`;
  }

  return roundIndex;
};
