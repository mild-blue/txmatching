import { BloodGroupEnumGenerated, DonorGenerated, PatientParametersGenerated, RecipientGenerated, SexEnumGenerated } from '../generated';
import { BloodGroup, Patient, PatientParameters, Sex } from '../model';
import { DEFAULT_LIST_ITEM } from '../components/list-item/list-item.interface';
import { parseAntigens } from '@app/parsers/hla.parsers';

export const parsePatient = ( data: DonorGenerated | RecipientGenerated ): Patient => {
  return {
    // TODO: https://github.com/mild-blue/txmatching/issues/401 create proper ListItem here
    ...DEFAULT_LIST_ITEM,
    dbId: data.db_id,
    medicalId: data.medical_id,
    parameters: parsePatientParameters(data.parameters)
  };
};


export const parsePatientParameters = ( data: PatientParametersGenerated ): PatientParameters => {
  return {
    bloodGroup: parseBloodGroup(data.blood_group),
    hlaTyping: parseAntigens(data.hla_typing),
    countryCode: data.country_code,
    sex: parsePatientSexType(data.sex),
    height: data.height,
    weight: data.weight,
    yearOfBirth: data.year_of_birth
  };
};


export const parsePatientSexType = (data: SexEnumGenerated | undefined): Sex | undefined => {
  return data !== undefined ? Sex[data] : undefined;
};


export const parseBloodGroup = (data: BloodGroupEnumGenerated): BloodGroup => {
  switch(data) {
    case BloodGroupEnumGenerated.A: return BloodGroup.A;
    case BloodGroupEnumGenerated.B: return BloodGroup.B;
    case BloodGroupEnumGenerated.Ab: return BloodGroup.AB;
    case BloodGroupEnumGenerated._0: return BloodGroup.ZERO;
    default: throw new Error(`Parsing blood group ${data} not implemented`);
  }
};
