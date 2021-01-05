export interface Version {
  environment: EnvironmentType;
  version: string;
}

export enum EnvironmentType {
  PRODUCTION = 'PRODUCTION',
  STAGING = 'STAGING',
  DEVELOPMENT = 'DEVELOPMENT',
  UNKNOWN = 'UNKNOWN'
}
