import { PatientPair } from '@app/model/PatientPair';
import { DetailedScorePerGroup } from '@app/model/Hla';
import { AllMessages } from '@app/model/Patient';

export interface Transplant extends PatientPair {
  score: number;
  maxScore: number;
  compatibleBlood: boolean;
  donor: string;
  recipient: string;
  detailedScorePerGroup: DetailedScorePerGroup[];
  transplantMessages: TransplantMessages;
}

export interface TransplantMessages {
  messageGlobal: string;
  allMessages: AllMessages;
}
