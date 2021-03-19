import { Patient } from '@app/model/Patient';
import { Antibodies } from '@app/model/Hla';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Recipient extends Patient {
  acceptableBloodGroups: BloodGroup[];
  cutoff?: number;
  waitingSince?: Date;
  previousTransplants?: number;
  hlaAntibodies: Antibodies;
  recipientRequirements?: RecipientRequirements;
  relatedDonorDbId: number;
}

export interface RecipientRequirements {
  requireBetterMatchInCompatibilityIndex: boolean;
  requireBetterMatchInCompatibilityIndexOrBloodGroup: boolean;
  requireCompatibleBloodGroup: boolean;

  [key: string]: boolean;
}
