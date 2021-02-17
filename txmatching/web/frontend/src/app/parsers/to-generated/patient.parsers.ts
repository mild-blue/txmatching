import { BloodGroupEnumGenerated, PatientModelToUpdateGenerated, SexEnumGenerated } from '../../generated';
import { BloodGroup, Sex } from '@app/model';
import { PatientEditable } from '@app/model/PatientEditable';

export const fromPatientEditable = ( patient: PatientEditable, patientId: number ): PatientModelToUpdateGenerated => {
  return {
    db_id: patientId,
    blood_group: fromBloodGroup(patient.bloodGroup),
    hla_typing: {
      hla_types_list: patient.antigens.map(raw_code => {return {raw_code};})
    },
    sex: fromSex(patient.sex),
    height: patient.height,
    weight: patient.weight,
    year_of_birth: patient.yearOfBirth,
  };
};

export const fromBloodGroup = ( bloodGroup: BloodGroup ): BloodGroupEnumGenerated => {
  switch (bloodGroup) {
    case BloodGroup.A: return BloodGroupEnumGenerated.A;
    case BloodGroup.B: return BloodGroupEnumGenerated.B;
    case BloodGroup.AB: return BloodGroupEnumGenerated.Ab;
    case BloodGroup.ZERO: return BloodGroupEnumGenerated._0;
    default: throw new Error(`Parsing from blood group ${bloodGroup} not implemented`);
  }
};

export const fromSex = ( sex: Sex ): SexEnumGenerated | undefined => {
  switch (sex) {
    case Sex.M: return SexEnumGenerated.M;
    case Sex.F: return SexEnumGenerated.F;
    case Sex.NULL: return undefined;
    default: throw new Error(`Parsing from sex ${sex} not implemented`);
  }
};
