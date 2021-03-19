import { Patient } from '@app/model/Patient';
import { AntibodiesPerGroup, Antibody, AntibodyRaw } from '@app/model/Hla';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Recipient extends Patient {
  acceptableBloodGroups: BloodGroup[];
  cutoff?: number;
  waitingSince?: Date;
  previousTransplants?: number;
  hlaAntibodies: {
    hlaAntibodiesList: Antibody[];
    hlaAntibodiesRawList: AntibodyRaw[];
    hlaAntibodiesPerGroups: AntibodiesPerGroup[];
  };
  recipientRequirements?: RecipientRequirements;
  relatedDonorDbId: number;
}

export interface RecipientRequirements {
  requireBetterMatchInCompatibilityIndex: boolean;
  requireBetterMatchInCompatibilityIndexOrBloodGroup: boolean;
  requireCompatibleBloodGroup: boolean;

  [key: string]: boolean;
}
