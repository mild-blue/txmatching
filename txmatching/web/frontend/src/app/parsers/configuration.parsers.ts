import { ConfigurationGenerated, ConfigurationIdGenerated } from "../generated";
import { Configuration, ConfigurationId } from "../model";

export const parseConfiguration = (data: ConfigurationGenerated): Configuration => {
  return {
    ...data,
  };
};

export const parseConfigurationId = (data: ConfigurationIdGenerated): ConfigurationId => {
  return {
    configId: data.config_id,
  };
};
