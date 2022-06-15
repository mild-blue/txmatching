import { ParsingIssueConfirmationGenerated } from '../generated';
import { ParsingIssueConfirmation } from '../model';

export const parseParsingIssueConfirmation = (data: ParsingIssueConfirmationGenerated): ParsingIssueConfirmation => {
  return {
    ...data
  };
};
