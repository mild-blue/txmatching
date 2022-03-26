import { ParsingErrorGenerated } from '../generated';
import { ParsingError } from '../model/ParsingError';

export const parseParsingError = (data: ParsingErrorGenerated): ParsingError => {
  return {
    hlaCodeOrGroup: data.hla_code_or_group,
    ParsingIssueDetail: data.parsing_issue_detail,
    message: data.message,
    donorId: data.donor_id,
    recipientId: data.recipient_id,
    eventId: data.txm_event_id
  };
};
