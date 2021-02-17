import { BloodGroupEnumGenerated, PatientModelToUpdateGenerated, SexEnumGenerated } from '../../generated';
import { BloodGroup } from '@app/model';
import { PatientEditable } from '@app/model/PatientEditable';

export const fromPatientEditable = ( patient: PatientEditable, patientId: number ): PatientModelToUpdateGenerated => {
  return {
    db_id: patientId,
    blood_group: fromBloodGroup(patient.bloodGroup),
    hla_typing: {
      hla_types_list: [] // TODOO: solve by donor.antigens not string but types
    },
    sex: patient.sex && SexEnumGenerated[patient.sex],
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
