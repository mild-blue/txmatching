import { DonorGenerated, PatientParametersGenerated, PatientParametersGeneratedSexEnum, RecipientGenerated } from '../generated/model';
import { Patient, PatientParameters, PatientSexType } from '../model';
import { ListItem, ListItemAbstractComponent, ListItemDetailAbstractComponent } from '../components/list-item/list-item.interface';
import { parseAntigen, parseHlaPerGroup } from '@app/parsers/hla.parsers';

const createDefaultListItem = (): ListItem => {
  return {
    index: 0,
    isActive: undefined,
    itemComponent: ListItemAbstractComponent,
    detailComponent: ListItemDetailAbstractComponent
  }
}

export const parsePatient = ( data: DonorGenerated | RecipientGenerated ): Patient => {
  return {
    ...createDefaultListItem(),
    db_id: data.db_id,
    medical_id: ":D" + data.medical_id,  // TODOO
    parameters: parsePatientParameters(data.parameters)
  };
};


export const parsePatientParameters = ( data: PatientParametersGenerated ): PatientParameters => {
  return {
    // TODO: create enum for blood group
    blood_group: data.blood_group ?? '',
    // TODO: create hla typing model
    hla_typing: {
      hla_per_groups: data.hla_typing?.hla_per_groups.map(_ => parseHlaPerGroup(_)) ?? [],
      hla_types_list: data.hla_typing?.hla_types_list.map(_ => parseAntigen(_)) ?? []
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
