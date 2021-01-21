import { Donor, PatientPair, Recipient } from '../model';
import { DEFAULT_LIST_ITEM } from '../components/list-item/list-item.interface';

export const getPatientPair = (donor?: Donor, recipient?: Recipient): PatientPair => {
  return {
    // TODO: create proper ListItem here
    ...DEFAULT_LIST_ITEM,
    d: donor,
    r: recipient
  };
};
