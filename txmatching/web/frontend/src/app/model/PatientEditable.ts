import { BloodGroup } from './Donor';
import { Country } from '@app/model/Country';
import { PatientSexType } from '@app/model/Patient';

export class PatientEditable {
  country?: Country = Country.Cze;
  medicalId: string = '';
  antigens: string[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  sex: PatientSexType = PatientSexType.M;
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

  setCountry(country: Country | undefined) {
    this.country = country;
  }
}

// export interface PatientUploadMessage {
//   recipients_uploaded: 0,
//   donors_uploaded: 0
// }
