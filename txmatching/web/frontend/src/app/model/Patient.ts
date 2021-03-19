import { ListItem } from '@app/components/list-item/list-item.interface';
import { Antigen, AntigenRaw, HlaPerGroup } from '@app/model/Hla';
import { Sex } from '@app/model/enums/Sex';
import { CountryCodeGenerated } from '@app/generated';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Patient extends ListItem {
  dbId: number;
  medicalId: string;
  parameters: PatientParameters;
}

export interface PatientParameters {
  bloodGroup: BloodGroup;
  hlaTyping: {
    hlaPerGroups: HlaPerGroup[];
    hlaTypesList: Antigen[];
    hlaTypesRawList: AntigenRaw[];
  };
  countryCode: CountryCodeGenerated;
  sex?: Sex;
  height?: number;
  weight?: number;
  yearOfBirth?: number;
}
