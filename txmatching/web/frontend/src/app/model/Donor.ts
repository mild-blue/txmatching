import { Patient } from '@app/model/Patient';

export interface Donor extends Patient {
  donor_type: DonorType;
  related_recipient_db_id: number;
}

export enum DonorType {
  DONOR = 'DONOR',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  NON_DIRECTED = 'NON_DIRECTED'
}
