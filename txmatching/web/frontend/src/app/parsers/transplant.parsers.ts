import { TransplantGenerated } from '../generated';
import { AntibodyMatchType, PatientList, Transplant } from '../model';
import { parseDetailedScorePerGroup } from './hla.parsers';
import { getPatientPair } from './patientPair.parsers';
import { DEFAULT_LIST_ITEM, ListItem } from '@app/components/list-item/list-item.interface';

export const parseTransplant = (data: TransplantGenerated, patients: PatientList, index: number): Transplant => {
  const foundDonor = patients.donors.find(p => p.medicalId === data.donor);
  const foundRecipient = patients.recipients.find(p => p.medicalId === data.recipient);
  const listItem: ListItem = {
    ...DEFAULT_LIST_ITEM,
    index
  };
  const patientPair = getPatientPair(listItem, foundDonor, foundRecipient);
  const detailed_score_per_group = data.detailed_score_per_group.map(parseDetailedScorePerGroup);

  return {
    ...patientPair,
    score: data.score,
    maxScore: data.max_score,
    compatibleBlood: data.compatible_blood,
    hasCrossmatch: data.has_crossmatch,
    donor: data.donor,
    recipient: data.recipient,
    detailedScorePerGroup: detailed_score_per_group
  };
};
