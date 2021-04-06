import { Patient } from '@app/model/Patient';
import { Antibodies } from '@app/model/Hla';
import { BloodGroup } from '@app/model/enums/BloodGroup';
import { ParsingError } from '@app/model/ParsingError';

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

export interface UpdatedRecipient {
  recipient: Recipient;
  parsingErrors: ParsingError[];
}
