import { Patient } from '@app/model/Patient';
import { DetailedScorePerGroup } from '@app/model/Hla';
import { DonorType } from '@app/model/enums/DonorType';

export interface Donor extends Patient {
  active: boolean;
  donor_type: DonorType;
  compatible_blood_with_related_recipient?: boolean;
  related_recipient_db_id?: number;
  score_with_related_recipient?: number;
  detailed_score_with_related_recipient: DetailedScorePerGroup[];
}

