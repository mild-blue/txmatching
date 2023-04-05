import { RecipientDonorCompatibilityDetail } from "@app/model/RecipientDonorCompatibilityDetail";
import { RecipientCompatibilityInfoJsonGenerated, RecipientDonorCompatibilityDetailsGenerated } from "../generated";
import { RecipientCompatibilityInfo } from "../model/RecipientCompatibilityInfo";
import { parseDetailedScorePerGroup } from "./hla.parsers";

export const parseRecipientCompatibilityInfo = (
  data: RecipientCompatibilityInfoJsonGenerated
): RecipientCompatibilityInfo => {
  return {
    cPRA: data.cPRA,
    compatibleDonors: data.compatible_donors,
    compatibleDonorsDetails: data.compatible_donors_details.map(parseRecipientDonorCompatibilityDetails),
  };
};

export const parseRecipientDonorCompatibilityDetails = (
  data: RecipientDonorCompatibilityDetailsGenerated
): RecipientDonorCompatibilityDetail => {
  return {
    compatibleBlood: data.compatible_blood,
    detailedScore: data.detailed_score.map(parseDetailedScorePerGroup),
    donorDbId: data.donor_db_id,
    maxScore: data.max_score,
    recipientDbId: data.recipient_db_id,
    score: data.score,
  };
};
