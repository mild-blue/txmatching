import {
  AntibodiesPerGroupGenerated,
  AntibodyMatchGenerated,
  AntibodyMatchGeneratedMatchTypeEnum,
  AntigenMatchGenerated,
  AntigenMatchGeneratedMatchTypeEnum,
  DetailedScoreForGroupGenerated,
  HlaAntibodyGenerated,
  HlaAntibodyRawGenerated,
  HlaCodesInGroupsGenerated,
  HlaTypeGenerated,
  HlaTypeRawGenerated
} from '../generated';
import {
  AntibodiesPerGroup,
  Antibody,
  AntibodyMatch,
  AntibodyMatchType,
  AntibodyRaw,
  Antigen,
  AntigenMatch,
  AntigenMatchType,
  AntigenRaw,
  DetailedScorePerGroup,
  Hla,
  HlaMatch,
  HlaPerGroup,
  HlaRaw
} from '../model';

export const parseHlaRaw = ( data: HlaTypeRawGenerated | HlaAntibodyGenerated ): HlaRaw => {
  return {
    raw_code: data.raw_code
  };
};

export const parseHla = ( data: HlaTypeGenerated | HlaAntibodyGenerated ): Hla => {
  return {
    ...parseHlaRaw(data),
    code: {
      displayCode: data.code.high_res ?? data.code.split ?? data.code.broad,
      highRes: data.code.high_res,
      split: data.code.split,
      broad: data.code.broad
    }
  };
};

export const parseAntigen = ( data: HlaTypeGenerated ): Antigen => {
  return {
    ...parseHla(data)
  };
};

export const parseAntigenRaw = ( data: HlaTypeRawGenerated ): AntigenRaw => {
  return {
    ...parseHlaRaw(data)
  };
};

export const parseAntibody = ( data: HlaAntibodyGenerated ): Antibody => {
  const {
    mfi,
    cutoff
  } = data;

  return {
    ...parseHla(data),
    mfi,
    cutoff
  };
};

export const parseAntibodyRaw = ( data: HlaAntibodyRawGenerated ): AntibodyRaw => {
  const {
    mfi,
    cutoff
  } = data;

  return {
    ...parseHlaRaw(data),
    mfi,
    cutoff
  };
};

export const parseDetailedScorePerGroup = ( data: DetailedScoreForGroupGenerated ): DetailedScorePerGroup => {
  return {
    hla_group: data.hla_group,
    donor_matches: data.donor_matches.map(parseAntigenMatch),
    recipient_matches: data.recipient_matches.map(parseAntigenMatch),
    antibody_matches: data.antibody_matches.map(parseAntibodyMatch),
    group_compatibility_index: data.group_compatibility_index
  };
};

export const parseHlaMatch = ( data: AntigenMatchGenerated | AntibodyMatchGenerated ): HlaMatch => {
  return {};
};

export const parseAntigenMatch = ( data: AntigenMatchGenerated ): AntigenMatch => {
  return {
    ...parseHlaMatch(data),
    hla_type: parseAntigen(data.hla_type),
    match_type: parseAntigenMatchType(data.match_type)
  };
};

export const parseAntibodyMatch = ( data: AntibodyMatchGenerated ): AntibodyMatch => {
  return {
    ...parseHlaMatch(data),
    hla_antibody: parseAntibody(data.hla_antibody),
    match_type: parseAntibodyMatchType(data.match_type)
  };
};

export const parseHlaPerGroup = ( data: HlaCodesInGroupsGenerated ): HlaPerGroup => {
  return {
    hla_group: data.hla_group,
    hla_types: data.hla_types.map(parseAntigen)
  };
};

export const parseAntibodiesPerGroup = ( data: AntibodiesPerGroupGenerated ): AntibodiesPerGroup => {
  return {
    hla_group: data.hla_group,
    hla_antibody_list: data.hla_antibody_list.map(parseAntibody)
  };
};

export const parseAntigenMatchType = ( data: AntigenMatchGeneratedMatchTypeEnum ): AntigenMatchType => {
  return AntigenMatchType[data];
};

export const parseAntibodyMatchType = ( data: AntibodyMatchGeneratedMatchTypeEnum ): AntibodyMatchType => {
  return AntibodyMatchType[data];
};
