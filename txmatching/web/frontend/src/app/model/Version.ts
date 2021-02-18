import { EnvironmentType } from '@app/model/enums/EnvironmentType';

export interface Version {
  environment: EnvironmentType;
  version: string;
}

