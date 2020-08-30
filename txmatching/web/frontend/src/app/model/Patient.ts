export interface Patient {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
  patient_type: PatientType;
}

export interface PatientParameters {
  blood_group: string;
  acceptable_blood_groups: string[];
  hla_antigens: string[];
  hla_antibodies: string[];
  country_code: string;
}

export enum PatientType {
  DONOR,
  RECIPIENT
}

export const patientsLSKey = 'patients';
