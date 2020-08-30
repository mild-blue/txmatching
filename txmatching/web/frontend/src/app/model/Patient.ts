export interface Patient {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
  patient_type: PatientType;
}

export interface PatientParameters {
  blood_group: string;
  acceptable_blood_groups: string[];
  hla_antigens: {
    codes: string[]
  };
  hla_antibodies: {
    codes: string[]
  };
  country_code: string;
}

export enum PatientType {
  DONOR = 'DONOR',
  RECIPIENT = 'RECIPIENT',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  ALTRUIST = 'ALTRUIST'
}

export const patientsLSKey = 'patients';

// recipient: [possible donors]
const compatibleBloodGroups: { [key: string]: string[] } = {
  '0': ['0'],
  'A': ['0', 'A'],
  'B': ['0', 'B'],
  'AB': ['0', 'A', 'B', 'AB']
};

const antigenMultipliers: { [key: string]: number } = {
  'A': 1,
  'B': 2,
  'DR': 9
};

export { compatibleBloodGroups, antigenMultipliers };
