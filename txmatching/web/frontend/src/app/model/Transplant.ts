import { PatientPair } from '@app/model/PatientPair';
import { DetailedCompatibilityIndex } from '@app/model/Hla';

export interface Transplant extends PatientPair {
  score: number;
  compatible_blood: boolean;
  donor: string;
  recipient: string;
  detailed_compatibility_index: DetailedCompatibilityIndex[];
}
