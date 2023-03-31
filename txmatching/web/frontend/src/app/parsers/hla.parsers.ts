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
  HLAAntibodyTypeGenerated,
  HlaCodeGenerated,
  HlaCodesInGroupsGenerated,
  HlaTypeGenerated,
  HlaTypeRawGenerated,
  HlaTypingGenerated,
} from "../generated";
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
  HlaCode,
  HlaMatch,
  HlaPerGroup,
  HlaRaw,
} from "../model";
import { HlaAntibodyType } from "@app/model/enums/HlaAntibodyType";

export const parseHlaRaw = (data: HlaTypeRawGenerated | HlaAntibodyGenerated): HlaRaw => {
  return {
    rawCode: data.raw_code,
  };
};

export const parseHla = (data: HlaTypeGenerated | HlaAntibodyGenerated): Hla => {
  return {
    ...parseHlaRaw(data),
    code: parseCode(data.code),
    displayCode: data.code.high_res ?? data.code.split ?? data.code.broad,
  };
};

export const parseAntigen = (data: HlaTypeGenerated): Antigen => {
  return {
    ...parseHla(data),
  };
};

export const parseAntigenRaw = (data: HlaTypeRawGenerated): AntigenRaw => {
  return {
    ...parseHlaRaw(data),
  };
};

export const parseCode = (data: HlaCodeGenerated): HlaCode => ({
  highRes: data.high_res,
  split: data.split,
  broad: data.broad,
});

export const parseAntibody = (data: HlaAntibodyGenerated): Antibody => {
  const { mfi, cutoff } = data;

  const rawCode = data.second_raw_code ? `${data.raw_code},${data.second_raw_code}` : data.raw_code;

  return {
    ...parseHlaRaw(data),
    displayCode: rawCode,
    code: {
      highRes: data.code.high_res,
      split: data.code.split,
      broad: data.code.broad,
    },
    mfi,
    cutoff,
    secondRawCode: data.second_raw_code,
    secondCode: data.second_code ? parseCode(data.second_code) : undefined,
    type: parseAntibodyType(data.type),
  };
};

export const parseAntibodyType = (data: HLAAntibodyTypeGenerated): HlaAntibodyType => {
  return HlaAntibodyType[data];
};

export const parseAntibodyRaw = (data: HlaAntibodyRawGenerated): AntibodyRaw => {
  const { mfi, cutoff } = data;

  return {
    ...parseHlaRaw(data),
    mfi,
    cutoff,
  };
};

export const parseAntigens = (hla_typing?: HlaTypingGenerated): Antigens => {
  return {
    hlaPerGroups: hla_typing?.hla_per_groups.map(parseHlaPerGroup) ?? [],
    hlaTypesRawList: hla_typing?.hla_types_raw_list.map(parseAntigenRaw) ?? [],
  };
};

export const parseAntibodies = (hla_antibodies?: HlaAntibodiesGenerated): Antibodies => {
  return {
    hlaAntibodiesRawList: hla_antibodies?.hla_antibodies_raw_list.map(parseAntibodyRaw) ?? [],
    hlaAntibodiesPerGroups: hla_antibodies?.hla_antibodies_per_groups.map(parseAntibodiesPerGroup) ?? [],
  };
};

export const parseDetailedScorePerGroup = (data: DetailedScoreForGroupGenerated): DetailedScorePerGroup => {
  return {
    hlaGroup: data.hla_group,
    donorMatches: data.donor_matches.map(parseAntigenMatch),
    recipientMatches: data.recipient_matches.map(parseAntigenMatch),
    antibodyMatches: data.antibody_matches.map(parseAntibodyMatch),
    groupCompatibilityIndex: data.group_compatibility_index,
  };
};

export const parseHlaMatch = (data: AntigenMatchGenerated | AntibodyMatchGenerated): HlaMatch => {
  return {};
};

export const parseAntigenMatch = (data: AntigenMatchGenerated): AntigenMatch => {
  return {
    ...parseHlaMatch(data),
    hlaType: parseAntigen(data.hla_type),
    matchType: parseAntigenMatchType(data.match_type),
  };
};

export const parseAntibodyMatch = (data: AntibodyMatchGenerated): AntibodyMatch => {
  return {
    ...parseHlaMatch(data),
    hlaAntibody: parseAntibody(data.hla_antibody),
    matchType: parseAntibodyMatchType(data.match_type),
  };
};

export const parseHlaPerGroup = (data: HlaCodesInGroupsGenerated): HlaPerGroup => {
  return {
    hlaGroup: data.hla_group,
    hlaTypes: data.hla_types.map(parseAntigen),
  };
};

export const parseAntibodiesPerGroup = (data: AntibodiesPerGroupGenerated): AntibodiesPerGroup => {
  return {
    hlaGroup: data.hla_group,
    hlaAntibodyList: data.hla_antibody_list.map(parseAntibody),
  };
};

export const parseAntigenMatchType = (data: AntigenMatchGeneratedMatchTypeEnum): AntigenMatchType => {
  return AntigenMatchType[data];
};

export const parseAntibodyMatchType = (data: AntibodyMatchGeneratedMatchTypeEnum): AntibodyMatchType => {
  return AntibodyMatchType[data];
};
