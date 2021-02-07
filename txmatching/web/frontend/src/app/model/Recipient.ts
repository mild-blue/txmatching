import { Patient } from '@app/model/Patient';
import { AntibodiesPerGroup, Antibody } from '@app/model/Hla';
import { BloodGroup, Sex } from '@app/model/Donor';

export interface Recipient extends Patient {
  acceptable_blood_groups: string[];
  hla_antibodies: {
    hla_antibodies_list: Antibody[];
    hla_antibodies_per_groups: AntibodiesPerGroup[];
  };
  recipient_requirements?: RecipientRequirements;
  related_donor_db_id: number;
}

export interface RecipientRequirements {
  require_better_match_in_compatibility_index: boolean;
  require_better_match_in_compatibility_index_or_blood_group: boolean;
  require_compatible_blood_group: boolean;

  [key: string]: boolean;
}

export class RecipientNew {
  medicalId: string = '';
  antigens: string[] = [];
  antibodies: Antibody[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  acceptableBloodGroups: string[] = [];
  sex: Sex = Sex.M;
  height?: number;
  weight?: number;
  yearOfBirth?: number;
  waitingSince: Date = new Date();
  previousTransplants: number = 0;

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
