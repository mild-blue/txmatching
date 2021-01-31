import { Patient } from '@app/model/Patient';
import { DetailedScorePerGroup } from '@app/model/Hla';

export interface Donor extends Patient {
  donor_type: DonorType;
  compatible_blood_with_related_recipient?: boolean;
  related_recipient_db_id?: number;
  score_with_related_recipient?: number;
  detailed_score_with_related_recipient: DetailedScorePerGroup[];
}

export class DonorNew {
  medicalId: string = '';
  antigens: string[] = [];
  bloodGroup: BloodGroup = BloodGroup.A;
  type: DonorType = DonorType.DONOR;
  sex: Sex = Sex.M;
  height?: number;
  weight?: number;
  yearOfBirth?: number;
  relatedRecipientMedicalId?: string;

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

export enum BloodGroup {
  A = 'A',
  B = 'B',
  AB = 'AB',
  ZERO = '0'
}

export enum Sex {
  F = 'F',
  M = 'M'
}

export enum DonorType {
  DONOR = 'DONOR',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  NON_DIRECTED = 'NON_DIRECTED'
}
