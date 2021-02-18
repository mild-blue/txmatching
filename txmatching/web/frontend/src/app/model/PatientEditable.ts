import { Country } from '@app/model/enums/Country';
import { BloodGroup } from '@app/model/enums/BloodGroup';
import { Sex } from '@app/model/enums/Sex';

export class PatientEditable {
  country?: Country = Country.Cze;
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

  setCountry(country: Country | undefined) {
    this.country = country;
  }
}
