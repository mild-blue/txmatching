import { DetailedScorePerGroup } from "./Hla";

export interface RecipientDonorCompatibilityDetail {
  compatibleBlood: boolean;
  detailedScore: Array<DetailedScorePerGroup>;
  donorDbId: number;
  maxScore: number;
  recipientDbId: number;
  score: number;
}
