import { Patient } from '@app/model/Patient';
import { DetailedScorePerGroup } from '@app/model/Hla';
import { DonorType } from '@app/model/enums/DonorType';

export interface Donor extends Patient {
  active: boolean;
  donorType: DonorType;
  compatibleBloodWithRelatedRecipient?: boolean;
  relatedRecipientDbId?: number;
  scoreWithRelatedRecipient?: number;
  maxScoreWithRelatedRecipient?: number;
  detailedScoreWithRelatedRecipient: DetailedScorePerGroup[];
}
