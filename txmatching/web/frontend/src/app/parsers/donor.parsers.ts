import { DonorGenerated, DonorTypeGenerated } from '../generated';
import { Donor, DonorType } from '../model';
import { parsePatient } from './patient.parsers';
import { parseDetailedScorePerGroup } from './hla.parsers';

export const parseDonor = (data: DonorGenerated): Donor => {
  return {
    ...parsePatient(data),
    active: data.active,
    donorType: parseDonorType(data.donor_type),
    compatibleBloodWithRelatedRecipient: data.compatible_blood_with_related_recipient,
    relatedRecipientDbId: data.related_recipient_db_id,
    scoreWithRelatedRecipient: data.score_with_related_recipient,
    maxScoreWithRelatedRecipient: data.max_score_with_related_recipient,
    detailedScoreWithRelatedRecipient: data.detailed_score_with_related_recipient?.map(parseDetailedScorePerGroup) ?? []
  };
};

export const parseDonorType = ( data: DonorTypeGenerated ): DonorType => {
  return DonorType[data];
};
