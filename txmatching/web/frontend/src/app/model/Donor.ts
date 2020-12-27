import { Patient } from '@app/model/Patient';
import { DetailedCompatibilityIndex } from '@app/model/Hla';

export interface Donor extends Patient {
  donor_type: DonorType;
  related_recipient_db_id: number;
  score_with_related_recipient: number;
  detailed_compatibility_index_with_related_recipient: DetailedCompatibilityIndex[];
}

export enum DonorType {
  DONOR = 'DONOR',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  NON_DIRECTED = 'NON_DIRECTED'
}
