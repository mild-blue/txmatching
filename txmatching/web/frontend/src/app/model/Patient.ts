import { ListItem } from '@app/components/list-item/list-item.interface';
import { Antigen, AntigenRaw, HlaPerGroup } from '@app/model/Hla';
import { Sex } from '@app/model/enums/Sex';
import { CountryCodeGenerated } from '@app/generated';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Patient extends ListItem {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
}

export interface PatientParameters {
  blood_group: BloodGroup;
  hla_typing: {
    hla_per_groups: HlaPerGroup[];
    hla_types_list: Antigen[];
    hla_types_raw_list: AntigenRaw[];
  };
  country_code: CountryCodeGenerated;
  sex?: Sex;
  height?: number;
  weight?: number;
  year_of_birth?: number;
}
