export interface Hla {
  code: string;
  raw_code: string;
}

export interface Antigen extends Hla {
}

export interface Antibody extends Hla {
  mfi: number;
  cutoff: number;
}

export interface DetailedScorePerGroup {
  hla_group: string;
  donor_matches: AntigenMatch[];
  recipient_matches: AntigenMatch[];
  antibody_matches: AntibodyMatch[];
  group_compatibility_index: number;
}

export interface HlaMatch {
  hla_code: string;
}

export interface AntigenMatch extends HlaMatch {
  match_type: AntigenMatchType;
}

export interface AntibodyMatch extends HlaMatch {
  match_type: AntibodyMatchType;
}

export interface HlaGroupCodes {
  hla_group: string;
  hla_codes: string[];
}

export enum AntigenMatchType {
  SPLIT = 'SPLIT',
  BROAD = 'BROAD',
  HIGH_RES = 'HIGH_RES',
  NONE = 'NONE',
}

export enum AntibodyMatchType {
  NONE = 'NONE',
  MATCH = 'MATCH',
}
