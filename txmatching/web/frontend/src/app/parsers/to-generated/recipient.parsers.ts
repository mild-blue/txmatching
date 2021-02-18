import { RecipientInputGenerated, RecipientModelToUpdateGenerated } from '../../generated';
import { fromBloodGroup, fromDateToString, fromPatientEditableToUpdateGenerated, fromSex } from './patient.parsers';
import { RecipientEditable } from '../../model/RecipientEditable';

/* Used for updating recipient */
export const fromRecipientEditableToUpdateGenerated = (recipient: RecipientEditable, recipientId: number ): RecipientModelToUpdateGenerated => {
  return {
    ...fromPatientEditableToUpdateGenerated(recipient, recipientId),
    acceptable_blood_groups: recipient.acceptableBloodGroups.map(fromBloodGroup),
    hla_antibodies: {
      hla_antibodies_list: recipient.antibodies
    },
    cutoff: recipient.antibodiesCutoff ? +recipient.antibodiesCutoff : undefined,
    // TODOO:
    // waitingSince - add to be
    // previousTransplants
    recipient_requirements: recipient.recipientRequirements
  };
};

/* Used for creating recipient */
// TODO: share logic with donor
export const fromRecipientEditableToInputGenerated = ( recipient: RecipientEditable ): RecipientInputGenerated => {
  return {
    acceptable_blood_groups: recipient.acceptableBloodGroups.map(fromBloodGroup),
    blood_group: fromBloodGroup(recipient.bloodGroup),
    height: recipient.height ? +recipient.height : undefined,
    hla_antibodies: recipient.antibodies.map(a => {
      return {
        name: a.raw_code,
        mfi: a.mfi,
        cutoff: recipient.antibodiesCutoff ? +recipient.antibodiesCutoff : 0
      };
    }),
    hla_typing: recipient.antigens.map(a => a.raw_code),
    medical_id: recipient.medicalId,
    previous_transplants: recipient.previousTransplants ? +recipient.previousTransplants : undefined,
    sex: recipient.sex ? fromSex(recipient.sex) : undefined,
    waiting_since: recipient.waitingSince ? fromDateToString(recipient.waitingSince) : undefined,
    weight: recipient.weight ? +recipient.weight : undefined,
    year_of_birth: recipient.yearOfBirth ? +recipient.yearOfBirth : undefined
  };
};
