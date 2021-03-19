import { VersionGenerated, VersionGeneratedEnvironmentEnum } from '../generated';
import { EnvironmentType, Version } from '../model';

export const parseVersion = (data: VersionGenerated): Version => {
  return {
    environment: parseEnvironmentType(data.environment),
    version: data.version
  };
};

export const parseEnvironmentType = (data: VersionGeneratedEnvironmentEnum): EnvironmentType => {
  return EnvironmentType[data];
};
