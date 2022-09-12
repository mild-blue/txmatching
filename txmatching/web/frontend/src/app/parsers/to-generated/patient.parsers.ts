import { BloodGroupEnumGenerated, PatientModelToUpdateGenerated, SexEnumGenerated } from "../../generated";
import { BloodGroup, Sex } from "@app/model";
import { PatientEditable } from "@app/model/PatientEditable";

/* Used for editing patient */
export const fromPatientEditableToUpdateGenerated = (
  patient: PatientEditable,
  patientId: number,
  patientUpdateId: number
): PatientModelToUpdateGenerated => {
  return {
    db_id: patientId,
    etag: patientUpdateId,
    blood_group: fromBloodGroup(patient.bloodGroup),
    hla_typing: {
      hla_types_list: patient.antigens.map((antigenEditable) => ({ raw_code: antigenEditable.rawCode })),
    },
    sex: patient.sex ? fromSex(patient.sex) : undefined,
    // TODO: convert values to numbers in SimpleNumberComponent, not here
    height: patient.height ? +patient.height : undefined,
    weight: patient.weight ? +patient.weight : undefined,
    year_of_birth: patient.yearOfBirth ? +patient.yearOfBirth : undefined,
    note: patient.note,
  };
};

export const fromBloodGroup = (bloodGroup: BloodGroup): BloodGroupEnumGenerated => {
  switch (bloodGroup) {
    case BloodGroup.A:
      return BloodGroupEnumGenerated.A;
    case BloodGroup.B:
      return BloodGroupEnumGenerated.B;
    case BloodGroup.AB:
      return BloodGroupEnumGenerated.Ab;
    case BloodGroup.ZERO:
      return BloodGroupEnumGenerated._0;
    default:
      throw new Error(`Parsing from blood group ${bloodGroup} not implemented`);
  }
};

export const fromSex = (sex: Sex): SexEnumGenerated | undefined => {
  switch (sex) {
    case Sex.M:
      return SexEnumGenerated.M;
    case Sex.F:
      return SexEnumGenerated.F;
    default:
      throw new Error(`Parsing from sex ${sex} not implemented`);
  }
};

export const fromDateToString = (date: Date): string => {
  const y = date.getFullYear();
  const d = date.getDate();
  const m = date.getMonth() + 1;
  const month = m < 10 ? `0${m}` : `${m}`;

  return `${y}-${month}-${d}`;
};
