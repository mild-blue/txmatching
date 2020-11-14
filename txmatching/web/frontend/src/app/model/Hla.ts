export interface Hla {
  code: string | null;
  raw_code: string;
}

export interface Antigen extends Hla {
}

export interface Antibody extends Hla {
  mfi: number;
}

export interface DetailedCompatibilityIndexForHlaGroup {
  donor_matches: Map<string, HlaMatchType>;
  recipient_matches: Map<string, HlaMatchType>;
  group_compatibility_index: number;
}

enum HlaMatchType {
  SPLIT = 'SPLIT',
  BROAD = 'BROAD',
  HIGH_RES = 'HIGH_RES'
}

// todo: delete?
export interface HlaCodesSorted {
  A: string[];
  B: string[];
  DR: string[];
  OTHER: string[];

  [key: string]: string[];
}

export interface HlaCodesScore {
  A: number;
  B: number;
  DR: number;

  [key: string]: number;
}
