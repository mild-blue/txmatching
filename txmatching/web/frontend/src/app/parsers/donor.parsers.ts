import { DonorGenerated, DonorTypeGenerated } from '../generated';
import { Donor, DonorType } from '../model';
import { parsePatient } from './patient.parsers';
import { parseDetailedScorePerGroup } from './hla.parsers';
import { ListItem } from '@app/components/list-item/list-item.interface';
import { PatientDonorItemComponent } from '@app/components/patient-donor-item/patient-donor-item.component';
import { PatientDonorDetailWrapperComponent } from '@app/components/patient-donor-detail-wrapper/patient-donor-detail-wrapper.component';

export const parseDonor = (data: DonorGenerated): Donor => {
  const donorListItem: ListItem = {
    index: 0,
    isActive: false,
    itemComponent: PatientDonorItemComponent,
    detailComponent: PatientDonorDetailWrapperComponent
  };

  return {
    ...parsePatient(data, donorListItem),
    active: data.active,
    donorType: parseDonorType(data.donor_type),
    compatibleBloodWithRelatedRecipient: data.compatible_blood_with_related_recipient,
    relatedRecipientDbId: data.related_recipient_db_id,
    scoreWithRelatedRecipient: data.score_with_related_recipient,
    maxScoreWithRelatedRecipient: data.max_score_with_related_recipient,
    detailedScoreWithRelatedRecipient: data.detailed_score_with_related_recipient?.map(parseDetailedScorePerGroup) ?? []
  };
};

export const parseDonorType = (data: DonorTypeGenerated): DonorType => {
  return DonorType[data];
};
