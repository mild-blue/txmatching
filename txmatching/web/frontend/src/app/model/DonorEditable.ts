import { Donor, DonorType } from './Donor';
import { PatientEditable } from './PatientEditable';

export class DonorEditable extends PatientEditable {
  type: DonorType = DonorType.DONOR;
  relatedRecipientMedicalId?: string; // TODOO: probably remove

  initializeFromPatient(donor: Donor) {
    super.initializeFromPatient(donor);
    this.type = donor.donor_type;
  }
}
