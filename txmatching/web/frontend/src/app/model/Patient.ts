export interface PatientList {
  donors: Patient[];
  recipients: Patient[];
}

export interface Patient {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
  donor_type: DonorType;
}

export interface PatientParameters {
  blood_group: string;
  acceptable_blood_groups: string[];
  hla_antigens: {
    codes: string[];
  };
  hla_antibodies: {
    codes: string[];
  };
  country_code: string;
}

export enum DonorType {
  DONOR = 'DONOR',
  BRIDGING_DONOR = 'BRIDGING_DONOR',
  ALTRUIST = 'ALTRUIST'
}

export const patientsLSKey = 'patients';
export const patientNameProperty = 'medical_id';

// recipient: [possible donors]
const compatibleBloodGroups: { [key: string]: string[]; } = {
  0: ['0'],
  A: ['0', 'A'],
  B: ['0', 'B'],
  AB: ['0', 'A', 'B', 'AB']
};

const antibodiesMultipliers: { [key: string]: number; } = {
  A: 1,
  B: 2,
  DR: 9
};

export { compatibleBloodGroups, antibodiesMultipliers };
