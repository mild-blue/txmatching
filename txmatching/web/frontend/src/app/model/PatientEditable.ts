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
  sex?: Sex = Sex.M;
  height?: number;
  weight?: number;
  yearOfBirth?: number;

  initializeFromPatient(patient: Patient) {
    this.country = patient.parameters.country_code;
    this.medicalId = patient.medical_id;
    this.antigens = [...patient.parameters.hla_typing.hla_types_list];
    this.bloodGroup = patient.parameters.blood_group;
    this.sex = patient.parameters.sex;
    this.height = patient.parameters.height;
    this.weight = patient.parameters.weight;
    this.yearOfBirth = patient.parameters.year_of_birth;
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
