import { ListItem } from '@app/components/list-item/list-item.interface';
import { Antigen, HlaGroupCodes } from '@app/model/Hla';

export interface Patient extends ListItem {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
}

export interface PatientParameters {
  blood_group: string;
  hla_typing: {
    codes_per_group: HlaGroupCodes[];
    hla_types_list: Antigen[];
  };
  country_code: string;
}

// recipient: [possible donors]
export const compatibleBloodGroups: { [key: string]: string[]; } = {
  0: ['0'],
  A: ['0', 'A'],
  B: ['0', 'B'],
  AB: ['0', 'A', 'B', 'AB']
};

export const antibodiesMultipliers: { [key: string]: number; } = {
  A: 1,
  B: 3,
  DR: 9
};
