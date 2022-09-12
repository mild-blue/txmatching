import { DonorEditable } from "../../model/DonorEditable";
import { RecipientEditable } from "../../model/RecipientEditable";
import { CountryCodeGenerated, DonorModelPairInGenerated } from "../../generated";
import { fromDonorEditableToInputGenerated } from "./donor.parsers";
import { DonorType } from "../../model";
import { fromRecipientEditableToInputGenerated } from "./recipient.parsers";

/* Used for creating patients */
export const fromPatientsEditableToInGenerated = (
  donor: DonorEditable,
  recipient: RecipientEditable
): DonorModelPairInGenerated => {
  const generated: DonorModelPairInGenerated = {
    // Assume same country for the donor and the recipient
    country_code: donor.country ?? CountryCodeGenerated.Cze,
    donor: fromDonorEditableToInputGenerated(donor),
  };

  if (donor.type.valueOf() === DonorType.DONOR.valueOf()) {
    generated.donor.related_recipient_medical_id = recipient.medicalId;
    generated.recipient = fromRecipientEditableToInputGenerated(recipient);
  }

  return generated;
};
