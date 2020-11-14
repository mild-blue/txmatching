import { Transplant } from '@app/model/Transplant';
import { DonorType } from './Donor';

export interface Round {
  index?: string;
  donorType: DonorType;
  transplants: Transplant[];
}
