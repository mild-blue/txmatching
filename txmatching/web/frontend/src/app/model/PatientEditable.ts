import { BloodGroup } from '@app/model/enums/BloodGroup';
import { Sex } from '@app/model/enums/Sex';
import { Patient } from '@app/model/Patient';
import { AntigenEditable } from '@app/model/HlaEditable';
import { CountryCodeGenerated } from '@app/generated';

export class PatientEditable {
  country?: CountryCodeGenerated = CountryCodeGenerated.Cze;
  medicalId: string = '';
  antigens: AntigenEditable[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  sex?: Sex;
  height?: number;
  weight?: number;
  yearOfBirth?: number;

  initializeFromPatient(patient: Patient) {
    this.country = patient.parameters.countryCode;
    this.medicalId = patient.medicalId;
    this.antigens = [...patient.parameters.hlaTyping.hlaTypesRawList];
    this.bloodGroup = patient.parameters.bloodGroup;
    this.sex = patient.parameters.sex;
    this.height = patient.parameters.height;
    this.weight = patient.parameters.weight;
    this.yearOfBirth = patient.parameters.yearOfBirth;
  }

  removeAntigen(a: AntigenEditable) {
    const index = this.antigens.indexOf(a);
    if (index !== -1) {
      this.antigens.splice(index, 1);
    }
  }

  addAntigen(a: AntigenEditable) {
    this.antigens.push(a);
  }

  setCountry(country?: CountryCodeGenerated) {
    this.country = country;
  }
}
