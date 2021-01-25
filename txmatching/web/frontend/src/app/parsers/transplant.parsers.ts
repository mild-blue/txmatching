import { TransplantGenerated } from '../generated';
import { PatientList, Transplant } from '../model';
import { parseDetailedScorePerGroup } from './hla.parsers';
import { getPatientPair } from './patientPair.parsers';
import { DEFAULT_LIST_ITEM, ListItem } from '@app/components/list-item/list-item.interface';

export const parseTransplant = (data: TransplantGenerated, patients: PatientList, index: number): Transplant => {
  const foundDonor = patients.donors.find(p => p.medical_id === data.donor);
  const foundRecipient = patients.recipients.find(p => p.medical_id === data.recipient);
  const listItem: ListItem = {
    ...DEFAULT_LIST_ITEM,
    index
  }

  return {
    ...getPatientPair(listItem, foundDonor, foundRecipient),
    score: data.score,
    compatible_blood: data.compatible_blood,
    donor: data.donor,
    recipient: data.recipient,
    detailed_score_per_group: data.detailed_score_per_group.map(parseDetailedScorePerGroup)
  };
};
