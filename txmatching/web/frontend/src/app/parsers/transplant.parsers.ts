import { TransplantGenerated, TransplantWarningGenerated } from '../generated';
import { PatientList, Transplant, TransplantMessages } from '../model';
import { parseDetailedScorePerGroup } from './hla.parsers';
import { getPatientPair } from './patientPair.parsers';
import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';

export const parseTransplant = (data: TransplantGenerated, patients: PatientList, index: number): Transplant => {
  const foundDonor = patients.donors.find(p => p.medicalId === data.donor);
  const foundRecipient = patients.recipients.find(p => p.medicalId === data.recipient);
  const listItem: ListItem = {
    index,
    isActive: false,
    itemComponent: PatientPairItemComponent,
    detailComponent: PatientPairDetailComponent
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
    detailedScorePerGroup: detailed_score_per_group,
    transplantMessages: parseTransplantMessages(data.transplant_messages)
  };
};

const parseTransplantMessages = (data: TransplantWarningGenerated | undefined): TransplantMessages => {
  if (!data) {
    return {
      messageGlobal: '',
      allMessages: {
        error: [],
        warning: [],
        info: []
      }
    };
  }

  return {
    messageGlobal: data.message_global ?? '',
    allMessages: {
      error: data.all_messages?.errors ?? [],
      warning: data.all_messages?.warnings ?? [],
      info: data.all_messages?.infos ?? []
    }
  };
};
