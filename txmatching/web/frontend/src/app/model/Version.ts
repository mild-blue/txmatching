import { ColourScheme } from '@app/model/enums/ColourScheme';
import { EnvironmentType } from '@app/model/enums/EnvironmentType';

export interface Version {
  colour_scheme: ColourScheme;
  environment: EnvironmentType;
  version: string;
}
