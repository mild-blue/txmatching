import { AllMessages, Patient } from '@app/model/Patient';
import { DetailedScorePerGroup } from '@app/model/Hla';
import { DonorType } from '@app/model/enums/DonorType';
import { ParsingError } from '@app/model/ParsingError';

export interface Donor extends Patient {
  active: boolean;
  donorType: DonorType;
  compatibleBloodWithRelatedRecipient?: boolean;
  relatedRecipientDbId?: number;
  scoreWithRelatedRecipient?: number;
  maxScoreWithRelatedRecipient?: number;
  detailedScoreWithRelatedRecipient: DetailedScorePerGroup[];
  allMessages: AllMessages;
}

export interface UpdatedDonor {
  donor: Donor;
  parsingErrors: ParsingError[];
}
