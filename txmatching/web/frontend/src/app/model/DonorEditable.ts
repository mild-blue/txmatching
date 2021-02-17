import { Donor } from './Donor';
import { PatientEditable } from './PatientEditable';
import { DonorType } from '@app/model/enums/DonorType';

export class DonorEditable extends PatientEditable {
  type: DonorType = DonorType.DONOR;
  relatedRecipientMedicalId?: string; // TODOO: probably remove
  active: boolean = true;

  initializeFromPatient(donor: Donor) {
    super.initializeFromPatient(donor);
    this.type = donor.donor_type;
    this.active = donor.active;
  }
}
