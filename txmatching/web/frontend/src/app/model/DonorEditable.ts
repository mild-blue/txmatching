import { DonorType } from './Donor';
import { PatientEditable } from './PatientEditable';

export class DonorEditable extends PatientEditable {
  type: DonorType = DonorType.DONOR;
  relatedRecipientMedicalId?: string;
}
