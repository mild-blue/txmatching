import { BloodGroup, Sex } from './Donor';

export class PatientEditable {
  medicalId: string = '';
  antigens: string[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  sex: Sex = Sex.M;
  height?: number;
  weight?: number;
  yearOfBirth?: number;

  removeAntigen(code: string) {
    const index = this.antigens.indexOf(code);
    if (index !== -1) {
      this.antigens.splice(index, 1);
    }
  }

  addAntigen(code: string) {
    this.antigens.push(code);
  }
}

// export interface PatientUploadMessage {
//   recipients_uploaded: 0,
//   donors_uploaded: 0
// }
