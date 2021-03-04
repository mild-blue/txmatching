import { ConfigurationGenerated } from '../generated';
import { AppConfiguration } from '../model';

export const parseAppConfiguration = (data: ConfigurationGenerated ): AppConfiguration => {
  return {
    ...data
  };
};
