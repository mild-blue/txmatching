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
  sex?: PatientSexType;
  height?: number;
  weight?: number;
  year_of_birth?: number;
}

export enum PatientSexType {
  M = 'M',
  F = 'F'
}
