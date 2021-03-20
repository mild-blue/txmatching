import { Donor } from './Donor';
import { PatientEditable } from './PatientEditable';
import { DonorType } from '@app/model/enums/DonorType';

export class DonorEditable extends PatientEditable {
  type: DonorType = DonorType.DONOR;
  active: boolean = true;

  initializeFromPatient(donor: Donor) {
    super.initializeFromPatient(donor);
    this.type = donor.donorType;
    this.active = donor.active;
  }
}
