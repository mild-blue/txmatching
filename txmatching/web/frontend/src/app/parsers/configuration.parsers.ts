import { ConfigurationGenerated } from "../generated";
import { Configuration } from "../model";

export const parseConfiguration = (data: ConfigurationGenerated): Configuration => {
  return {
    ...data,
  };
};
