import { ListItem } from '@app/components/list-item/list-item.interface';
import { Donor } from '@app/model/Donor';
import { Recipient } from '@app/model/Recipient';

export interface PatientPair extends ListItem {
  d?: Donor;
  r?: Recipient;
}
