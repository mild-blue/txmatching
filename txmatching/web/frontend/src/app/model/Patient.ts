import { Antigens } from '@app/model/Hla';
import { Sex } from '@app/model/enums/Sex';
import { CountryCodeGenerated } from '@app/generated';
import { BloodGroup } from '@app/model/enums/BloodGroup';
import { NewListItem } from '@app/pages/abstract-list/abstract-list.component';

export interface Patient extends NewListItem {
  dbId: number;
  medicalId: string;
  parameters: PatientParameters;
}

export interface PatientParameters {
  bloodGroup: BloodGroup;
  hlaTyping: Antigens;
  countryCode: CountryCodeGenerated;
  sex?: Sex;
  height?: number;
  weight?: number;
  yearOfBirth?: number;
}
