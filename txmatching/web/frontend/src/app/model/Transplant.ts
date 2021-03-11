import { PatientPair } from '@app/model/PatientPair';
import { DetailedScorePerGroup } from '@app/model/Hla';

export interface Transplant extends PatientPair {
  score: number;
  compatible_blood: boolean;
  hasCrossmatch: boolean;
  donor: string;
  recipient: string;
  detailed_score_per_group: DetailedScorePerGroup[];
}
