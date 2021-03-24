import { Donor, PatientPair, Recipient } from '../model';
import { ListItem } from '../components/list-item/list-item.interface';

export const getPatientPair = (listItem: ListItem, donor?: Donor, recipient?: Recipient): PatientPair => {
  return {
    ...listItem,
    d: donor,
    r: recipient
  };
};
