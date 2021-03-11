import { PatientPair } from '@app/model/PatientPair';
import { DetailedScorePerGroup } from '@app/model/Hla';

export interface Transplant extends PatientPair {
  score: number;
  maxScore: number;
  compatible_blood: boolean;
  donor: string;
  recipient: string;
  detailed_score_per_group: DetailedScorePerGroup[];
}
