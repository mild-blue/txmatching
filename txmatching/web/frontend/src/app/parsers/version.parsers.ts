import { VersionGenerated, VersionGeneratedColourSchemeEnum, VersionGeneratedEnvironmentEnum } from '../generated';
import { ColourScheme, EnvironmentType, Version } from '../model';

export const parseVersion = (data: VersionGenerated): Version => {
  return {
    colour_scheme: parseColourScheme(data.colour_scheme),
    environment: parseEnvironmentType(data.environment),
    version: data.version
  };
};

export const parseEnvironmentType = (data: VersionGeneratedEnvironmentEnum): EnvironmentType => {
  return EnvironmentType[data];
};

export const parseColourScheme = (data: VersionGeneratedColourSchemeEnum): ColourScheme => {
  return ColourScheme[data];
};
