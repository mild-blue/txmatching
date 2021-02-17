import { BloodGroup, Sex } from './Donor';
import { Country } from '@app/model/Country';
import { Patient } from '@app/model/Patient';

export class PatientEditable {
  country: Country = Country.Cze;
  medicalId: string = '';
  antigens: string[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  sex?: Sex = Sex.M;  // TODOO: change by merge
  height?: number;
  weight?: number;
  yearOfBirth?: number;

  initializeFromPatient(patient: Patient) {
    this.country = Country.Cze;
    this.medicalId = patient.medical_id;
    this.antigens = patient.parameters.hla_typing.hla_types_list.map(antigen => antigen.raw_code);
    this.bloodGroup = BloodGroup.A; //this.item.parameters.blood_group,
    this.sex = patient.parameters.sex && Sex[patient.parameters.sex]; // TODOO
    this.height = patient.parameters.height;
    this.weight = patient.parameters.weight;
    this.yearOfBirth = patient.parameters.year_of_birth;
  }

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
