import { ParsingIssueGenerated } from '../generated'; 
import { ParsingIssue } from '../model/ParsingIssue';

export const parseParsingIssue = (data: ParsingIssueGenerated): ParsingIssue => {
  return {
    confirmedAt: data.confirmed_at,
    confirmedBy: data.confirmed_by ?? undefined,
    dbId: data.db_id,
    donorId: data.donor_id,
    hlaCodeOrGroup: data.hla_code_or_group,
    message: data.message,
    parsingIssueDetail: data.parsing_issue_detail,
    recipientId: data.recipient_id,
    txmEventId: data.txm_event_id
  };
};
