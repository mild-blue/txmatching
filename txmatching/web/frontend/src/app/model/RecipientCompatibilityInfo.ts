import { RecipientDonorCompatibilityDetail } from "./RecipientDonorCompatibilityDetail";

export interface RecipientCompatibilityInfo {
  cPRA: number;
  compatibleDonors: Array<number>;
  compatibleDonorsDetails: Array<RecipientDonorCompatibilityDetail>;
}
