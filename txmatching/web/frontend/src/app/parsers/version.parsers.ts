import { VersionGenerated, VersionGeneratedColourSchemeEnum, VersionGeneratedEnvironmentEnum } from '../generated';
import { ColourScheme, EnvironmentType, Version } from '../model';

export const parseVersion = (data: VersionGenerated): Version => {
  console.log('im here in parse version', parseEnvironmentType(data.environment), 'from', data.environment, parseColourScheme(data.colour_scheme), 'from', data.colour_scheme);
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
