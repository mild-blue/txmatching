import { PatientPair } from '@app/model/PatientPair';
import { DetailedScorePerGroup } from '@app/model/Hla';

export interface Transplant extends PatientPair {
  score: number;
  maxScore: number;
  compatibleBlood: boolean;
  hasCrossmatch: boolean;
  donor: string;
  recipient: string;
  detailedScorePerGroup: DetailedScorePerGroup[];
  transplantMessages: TransplantMessages;
}

export interface TransplantMessages {
  messageGlobal: string;
  allMessages: {
    error: string[];
    warning: string[];
    info: string[];
  }
}
