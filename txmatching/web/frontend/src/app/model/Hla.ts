import { AntigenMatchType } from '@app/model/enums/AntigenMatchType';
import { AntibodyMatchType } from '@app/model/enums/AntibodyMatchType';

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

export class AntibodyEditable {
  raw_code?: string; // TODOO: test that name->raw_code renaming still works
  mfi?: number;
  cutoff?: number;
}

export interface DetailedScorePerGroup {
  hla_group: string;
  donor_matches: AntigenMatch[];
  recipient_matches: AntigenMatch[];
  antibody_matches: AntibodyMatch[];
  group_compatibility_index: number;
}

export interface HlaMatch {
}

export interface AntigenMatch extends HlaMatch {
  hla_type: Antigen;
  match_type: AntigenMatchType;
}

export interface AntibodyMatch extends HlaMatch {
  hla_antibody: Antibody;
  match_type: AntibodyMatchType;
}

export interface HlaPerGroup {
  hla_group: string;
  hla_types: Antigen[];
}

export interface AntibodiesPerGroup {
  hla_group: string;
  hla_antibody_list: Antibody[];
}
