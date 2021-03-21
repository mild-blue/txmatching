import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';
import { NewListItem } from '@app/pages/abstract-list/abstract-list.component';

export interface PatientPair extends NewListItem {
  d?: Donor;
  r?: Recipient;
}
