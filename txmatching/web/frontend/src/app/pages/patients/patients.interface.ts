import { ListItemAbstractComponent, ListItemDetailAbstractComponent } from '@app/components/list-item/list-item.interface';
import { PatientPairItemComponent } from '@app/components/patient-pair-item/patient-pair-item.component';
import { PatientPairDetailComponent } from '@app/components/patient-pair-detail/patient-pair-detail.component';
import { PatientItemComponent } from '@app/components/patient-item/patient-item.component';
import { PatientDetailDonorComponent } from '@app/components/patient-detail-donor/patient-detail-donor.component';
import { PatientDetailRecipientComponent } from '@app/components/patient-detail-recipient/patient-detail-recipient.component';

export enum PatientListFilterType {
  Pairs = 'pairs',
  Donors = 'donors',
  Recipients = 'recipients'
}

export interface PatientListFilter {
  type: PatientListFilterType;
  itemComponent: typeof ListItemAbstractComponent;
  detailComponent: typeof ListItemDetailAbstractComponent;
}

export const patientListFilters: PatientListFilter[] = [
  { type: PatientListFilterType.Pairs, itemComponent: PatientPairItemComponent, detailComponent: PatientPairDetailComponent },
  { type: PatientListFilterType.Donors, itemComponent: PatientItemComponent, detailComponent: PatientDetailDonorComponent },
  { type: PatientListFilterType.Recipients, itemComponent: PatientItemComponent, detailComponent: PatientDetailRecipientComponent }
];
