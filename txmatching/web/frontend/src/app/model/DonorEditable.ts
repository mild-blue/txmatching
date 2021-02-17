import { PatientEditable } from './PatientEditable';
import { DonorType } from '@app/model/enums/DonorType';

export class DonorEditable extends PatientEditable {
  type: DonorType = DonorType.DONOR;
  relatedRecipientMedicalId?: string;
}
