import { ListItem } from '@app/components/list-item/list-item.interface';
import { Antigens } from '@app/model/Hla';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';
import { Sex } from '@app/model/enums/Sex';
import { CountryCodeGenerated } from '@app/generated';
import { BloodGroup } from '@app/model/enums/BloodGroup';

export interface Patient extends ListItem {
  dbId: number;
  medicalId: string;
  parameters: PatientParameters;
  updateId: number;
}

export interface PatientParameters {
  bloodGroup: BloodGroup;
  hlaTyping: Antigens;
  countryCode: CountryCodeGenerated;
  sex?: Sex;
  height?: number;
  weight?: number;
  yearOfBirth?: number;
  note: string;
}

export interface AllMessages {
  error: ParsingIssueConfirmation[];
  warning: ParsingIssueConfirmation[];
  info: ParsingIssueConfirmation[];
}

export interface AllTransplantMessages {
  error: string[];
  warning: string[];
  info: string[];
}
