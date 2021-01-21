import { DonorGenerated, PatientParametersGenerated, PatientParametersGeneratedSexEnum, RecipientGenerated } from '../generated';
import { Patient, PatientParameters, PatientSexType } from '../model';
import { DEFAULT_LIST_ITEM } from '../components/list-item/list-item.interface';
import { parseAntigen, parseHlaPerGroup } from '@app/parsers/hla.parsers';

export const parsePatient = ( data: DonorGenerated | RecipientGenerated ): Patient => {
  return {
    // TODO: create proper ListItem here
    ...DEFAULT_LIST_ITEM,
    db_id: data.db_id,
    medical_id: data.medical_id,
    parameters: parsePatientParameters(data.parameters)
  };
};


export const parsePatientParameters = ( data: PatientParametersGenerated ): PatientParameters => {
  return {
    // TODO: create enum for blood group
    blood_group: data.blood_group ?? '',
    // TODO: create hla typing model
    hla_typing: {
      hla_per_groups: data.hla_typing?.hla_per_groups.map(parseHlaPerGroup) ?? [],
      hla_types_list: data.hla_typing?.hla_types_list.map(parseAntigen) ?? []
    },
    // TODO: create enum for country code
    country_code: data.country_code ?? '',
    sex: parsePatientSexType(data.sex),
    height: data.height,
    weight: data.weight,
    year_of_birth: data.year_of_birth
  }
};


export const parsePatientSexType = ( data: PatientParametersGeneratedSexEnum | undefined ): PatientSexType | undefined => {
  return data !== undefined ? PatientSexType[data] : undefined;
};
