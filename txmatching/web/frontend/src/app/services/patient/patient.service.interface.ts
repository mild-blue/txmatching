import { DonorEditable } from "@app/model/DonorEditable";
import { RecipientEditable } from "@app/model/RecipientEditable";

export interface PatientPairToAdd {
  donor: DonorEditable;
  recipient: RecipientEditable;
}
