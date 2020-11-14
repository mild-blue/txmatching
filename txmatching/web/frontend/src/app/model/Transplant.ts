import { PatientPair } from '@app/model/PatientPair';
import { DetailedCompatibilityIndexForHlaGroup } from '@app/model/Hla';

// TODO: remove question marks
export interface Transplant extends PatientPair {
  score?: number;
  compatible_blood?: boolean;
  donor?: string;
  recipient?: string;

  detailed_compatibility_index?: Map<string, DetailedCompatibilityIndexForHlaGroup>;

  // todo delete
  // antigens_score?: HlaCodesScore;
  //
  // donor_antigens?: HlaCodesSorted;
  // recipient_antigens?: HlaCodesSorted;
  // recipient_antibodies?: HlaCodesSorted;
}
