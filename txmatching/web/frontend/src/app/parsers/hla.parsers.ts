import {
  AntibodiesPerGroupGenerated,
  AntibodyMatchGenerated,
  AntibodyMatchGeneratedMatchTypeEnum,
  AntigenMatchGenerated,
  AntigenMatchGeneratedMatchTypeEnum,
  DetailedScoreForGroupGenerated,
  HlaAntibodiesGenerated,
  HlaAntibodyGenerated,
  HlaAntibodyRawGenerated,
  HlaCodesInGroupsGenerated,
  HlaTypeGenerated,
  HlaTypeRawGenerated,
  HlaTypingGenerated
} from '../generated';
import {
  Antibodies,
  AntibodiesPerGroup,
  Antibody,
  AntibodyMatch,
  AntibodyMatchType,
  AntibodyRaw,
  Antigen,
  AntigenMatch,
  AntigenMatchType,
  AntigenRaw,
  Antigens,
  DetailedScorePerGroup,
  Hla,
  HlaMatch,
  HlaPerGroup,
  HlaRaw
} from '../model';

export const parseHlaRaw = ( data: HlaTypeRawGenerated | HlaAntibodyGenerated ): HlaRaw => {
  return {
    rawCode: data.raw_code
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

export const parseAntigens = ( hla_typing?: HlaTypingGenerated ): Antigens => {
  return {
    hlaPerGroups: hla_typing?.hla_per_groups.map(parseHlaPerGroup) ?? [],
    hlaTypesList: hla_typing?.hla_types_list.map(parseAntigen) ?? [],
    hlaTypesRawList: hla_typing?.hla_types_raw_list.map(parseAntigenRaw) ?? []
  };
};

export const parseAntibodies = ( hla_antibodies?: HlaAntibodiesGenerated ): Antibodies => {
  return {
    hlaAntibodiesList: hla_antibodies?.hla_antibodies_list.map(parseAntibody) ?? [],
    hlaAntibodiesRawList: hla_antibodies?.hla_antibodies_raw_list.map(parseAntibodyRaw) ?? [],
    hlaAntibodiesPerGroups: hla_antibodies?.hla_antibodies_per_groups.map(parseAntibodiesPerGroup) ?? []
  };
};

export const parseDetailedScorePerGroup = ( data: DetailedScoreForGroupGenerated ): DetailedScorePerGroup => {
  return {
    hlaGroup: data.hla_group,
    donorMatches: data.donor_matches.map(parseAntigenMatch),
    recipientMatches: data.recipient_matches.map(parseAntigenMatch),
    antibodyMatches: data.antibody_matches.map(parseAntibodyMatch),
    groupCompatibilityIndex: data.group_compatibility_index
  };
};

export const parseHlaMatch = ( data: AntigenMatchGenerated | AntibodyMatchGenerated ): HlaMatch => {
  return {};
};

export const parseAntigenMatch = ( data: AntigenMatchGenerated ): AntigenMatch => {
  return {
    ...parseHlaMatch(data),
    hlaType: parseAntigen(data.hla_type),
    matchType: parseAntigenMatchType(data.match_type)
  };
};

export const parseAntibodyMatch = ( data: AntibodyMatchGenerated ): AntibodyMatch => {
  return {
    ...parseHlaMatch(data),
    hlaAntibody: parseAntibody(data.hla_antibody),
    matchType: parseAntibodyMatchType(data.match_type)
  };
};

export const parseHlaPerGroup = ( data: HlaCodesInGroupsGenerated ): HlaPerGroup => {
  return {
    hlaGroup: data.hla_group,
    hlaTypes: data.hla_types.map(parseAntigen)
  };
};

export const parseAntibodiesPerGroup = ( data: AntibodiesPerGroupGenerated ): AntibodiesPerGroup => {
  return {
    hlaGroup: data.hla_group,
    hlaAntibodyList: data.hla_antibody_list.map(parseAntibody)
  };
};

export const parseAntigenMatchType = ( data: AntigenMatchGeneratedMatchTypeEnum ): AntigenMatchType => {
  return AntigenMatchType[data];
};

export const parseAntibodyMatchType = ( data: AntibodyMatchGeneratedMatchTypeEnum ): AntibodyMatchType => {
  return AntibodyMatchType[data];
};
