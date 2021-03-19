import { AntigenMatchType } from '@app/model/enums/AntigenMatchType';
import { AntibodyMatchType } from '@app/model/enums/AntibodyMatchType';

export interface HlaRaw {
  rawCode: string;
}

export interface HlaCode {
  displayCode: string;

  highRes?: string;
  split?: string;
  broad: string;
}

export interface Hla extends HlaRaw {
  code: HlaCode;
}

export interface Antigen extends Hla {
}

export interface AntigenRaw extends HlaRaw {
}

export interface Antibody extends Hla {
  mfi: number;
  cutoff: number;
}

export interface AntibodyRaw extends HlaRaw {
  mfi: number;
  cutoff: number;
}

export interface Antigens {
  hlaPerGroups: HlaPerGroup[];
  hlaTypesRawList: AntigenRaw[];
}

export interface Antibodies {
  hlaAntibodiesRawList: AntibodyRaw[];
  hlaAntibodiesPerGroups: AntibodiesPerGroup[];
}

export interface DetailedScorePerGroup {
  hlaGroup: string;
  donorMatches: AntigenMatch[];
  recipientMatches: AntigenMatch[];
  antibodyMatches: AntibodyMatch[];
  groupCompatibilityIndex: number;
}

export interface HlaMatch {
}

export interface AntigenMatch extends HlaMatch {
  hlaType: Antigen;
  matchType: AntigenMatchType;
}

export interface AntibodyMatch extends HlaMatch {
  hlaAntibody: Antibody;
  matchType: AntibodyMatchType;
}

export interface HlaPerGroup {
  hlaGroup: string;
  hlaTypes: Antigen[];
}

export interface AntibodiesPerGroup {
  hlaGroup: string;
  hlaAntibodyList: Antibody[];
}
