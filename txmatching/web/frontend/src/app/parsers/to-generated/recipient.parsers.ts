import { RecipientInputGenerated, RecipientModelToUpdateGenerated } from "../../generated";
import { fromBloodGroup, fromDateToString, fromPatientEditableToUpdateGenerated, fromSex } from "./patient.parsers";
import { RecipientEditable } from "../../model/RecipientEditable";

/* Used for updating recipient */
export const fromRecipientEditableToUpdateGenerated = (
  recipient: RecipientEditable,
  recipientId: number,
  recipientUpdateId: number
): RecipientModelToUpdateGenerated => {
  return {
    ...fromPatientEditableToUpdateGenerated(recipient, recipientId, recipientUpdateId),
    acceptable_blood_groups: recipient.acceptableBloodGroups.map(fromBloodGroup),
    hla_antibodies: {
      hla_antibodies_list: recipient.antibodies.map((antibodyEditable) => ({
        raw_code: antibodyEditable.rawCode,
        mfi: antibodyEditable.mfi,
      })),
    },
    cutoff: recipient.antibodiesCutoff ? +recipient.antibodiesCutoff : undefined,
    waiting_since: recipient.waitingSince ? fromDateToString(recipient.waitingSince) : undefined,
    // TODO: convert value to number in SimpleNumberComponent, not here
    previous_transplants: recipient.previousTransplants ? +recipient.previousTransplants : undefined,
    recipient_requirements: {
      require_better_match_in_compatibility_index:
        recipient.recipientRequirements.requireBetterMatchInCompatibilityIndex,
      require_better_match_in_compatibility_index_or_blood_group:
        recipient.recipientRequirements.requireBetterMatchInCompatibilityIndexOrBloodGroup,
      require_compatible_blood_group: recipient.recipientRequirements.requireCompatibleBloodGroup,
      max_donor_age: recipient.recipientRequirements.maxDonorAge,
      min_donor_age: recipient.recipientRequirements.minDonorAge,
      max_donor_weight: recipient.recipientRequirements.maxDonorWeight,
      min_donor_weight: recipient.recipientRequirements.minDonorWeight,
      max_donor_height: recipient.recipientRequirements.maxDonorHeight,
      min_donor_height: recipient.recipientRequirements.minDonorHeight,
    },
  };
};

/* Used for creating recipient */
// TODO: share logic with donor
export const fromRecipientEditableToInputGenerated = (recipient: RecipientEditable): RecipientInputGenerated => {
  return {
    acceptable_blood_groups: recipient.acceptableBloodGroups.map(fromBloodGroup),
    blood_group: fromBloodGroup(recipient.bloodGroup),
    height: recipient.height ? +recipient.height : undefined,
    hla_antibodies: recipient.antibodies.map((a) => {
      return {
        name: a.rawCode,
        mfi: a.mfi,
        cutoff: recipient.antibodiesCutoff ? +recipient.antibodiesCutoff : 0,
      };
    }),
    hla_typing: recipient.antigens.map((a) => a.rawCode),
    medical_id: recipient.medicalId,
    previous_transplants: recipient.previousTransplants ? +recipient.previousTransplants : undefined,
    sex: recipient.sex ? fromSex(recipient.sex) : undefined,
    note: recipient.note,
    waiting_since: recipient.waitingSince ? fromDateToString(recipient.waitingSince) : undefined,
    weight: recipient.weight ? +recipient.weight : undefined,
    year_of_birth: recipient.yearOfBirth ? +recipient.yearOfBirth : undefined,
  };
};
