import { RecipientModelToUpdateGenerated } from '../../generated';
import { fromPatientEditable } from './patient.parsers';
import { RecipientEditable } from '../../model/RecipientEditable';

export const fromRecipientEditable = ( recipient: RecipientEditable, recipientId: number ): RecipientModelToUpdateGenerated => {
  return {
    ...fromPatientEditable(recipient, recipientId),
    acceptable_blood_groups: [], //recipient.acceptableBloodGroups, // TODOO change from string
    hla_antibodies: {
      hla_antibodies_list: []//recipient.antibodies TODOO
    },
    // recipient_requirements: recipient.recipient_requirements, // TODOO: add recipient_requirements to editable
    cutoff: recipient.antibodiesCutoff,
    recipient_requirements: recipient.recipientRequirements
  };
};
