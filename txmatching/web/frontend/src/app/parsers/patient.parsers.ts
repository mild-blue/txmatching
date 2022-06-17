import {
  AllMessagesGenerated,
  BloodGroupEnumGenerated,
  DonorGenerated,
  PatientParametersGenerated,
  RecipientGenerated,
  SexEnumGenerated
} from '../generated';
import { AllMessages, BloodGroup, Patient, PatientParameters, Sex } from '../model';
import { ListItem } from '../components/list-item/list-item.interface';
import { parseAntigens } from '@app/parsers/hla.parsers';
import { parseParsingIssueConfirmation } from './parsingIssueConfirmation.parsers';
import { ParsingIssueConfirmation } from '@app/model/ParsingIssueConfirmation';

export const parsePatient = (data: DonorGenerated | RecipientGenerated, listItem: ListItem): Patient => {
  return {
    ...listItem,
    dbId: data.db_id,
    medicalId: data.medical_id,
    parameters: parsePatientParameters(data.parameters),
    updateId: data.etag
  };
};


export const parsePatientParameters = (data: PatientParametersGenerated): PatientParameters => {
  return {
    bloodGroup: parseBloodGroup(data.blood_group),
    hlaTyping: parseAntigens(data.hla_typing),
    countryCode: data.country_code,
    sex: parsePatientSexType(data.sex),
    height: data.height,
    weight: data.weight,
    yearOfBirth: data.year_of_birth,
    note: data.note
  };
};


export const parsePatientSexType = (data: SexEnumGenerated | undefined): Sex | undefined => {
  return data !== undefined ? Sex[data] : undefined;
};


export const parseBloodGroup = (data: BloodGroupEnumGenerated): BloodGroup => {
  switch (data) {
    case BloodGroupEnumGenerated.A:
      return BloodGroup.A;
    case BloodGroupEnumGenerated.B:
      return BloodGroup.B;
    case BloodGroupEnumGenerated.Ab:
      return BloodGroup.AB;
    case BloodGroupEnumGenerated._0:
      return BloodGroup.ZERO;
    default:
      throw new Error(`Parsing blood group ${data} not implemented`);
  }
};

export const parseAllMessages = (allMessages: AllMessagesGenerated | undefined): AllMessages => {
  const errors: ParsingIssueConfirmation[] = [];
  const warnings: ParsingIssueConfirmation[] = [];
  const infos: ParsingIssueConfirmation[] = [];

  allMessages?.errors?.forEach((error) => {
    errors.push(parseParsingIssueConfirmation(error));
  });

  allMessages?.warnings?.forEach((warning) => {
    warnings.push(parseParsingIssueConfirmation(warning));
  });

  warnings.sort((warning) => (!warning.confirmed_by) ? -1 : 1);

  allMessages?.infos?.forEach((info) => {
    infos.push(parseParsingIssueConfirmation(info));
  });

  return {
    error: errors,
    warning: warnings,
    info: infos
  };
};
