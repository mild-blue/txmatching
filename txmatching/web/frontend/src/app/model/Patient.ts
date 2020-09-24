export interface PatientList {
  donors: Donor[];
  recipients: Recipient[];
}

export interface Patient {
  db_id: number;
  medical_id: string;
  parameters: PatientParameters;
}

export interface Recipient extends Patient {
  acceptable_blood_groups: string[];
  hla_antibodies: {
    codes: string[];
  };
}

export interface Donor extends Patient {
  donor_type: DonorType;
  related_donor_db_id: number;
}

export interface PatientParameters {
  blood_group: string;
  hla_typing: {
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
