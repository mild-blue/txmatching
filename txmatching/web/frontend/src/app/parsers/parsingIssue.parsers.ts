import { ParsingIssueGenerated } from '../generated';
import { ParsingIssue } from '../model/ParsingIssue';

export const parseParsingIssue = (data: ParsingIssueGenerated): ParsingIssue => {
  return {
    hlaCodeOrGroup: data.hla_code_or_group,
    ParsingIssueDetail: data.parsing_issue_detail,
    message: data.message,
    donorId: data.donor_id,
    recipientId: data.recipient_id,
    eventId: data.txm_event_id
  };
};
