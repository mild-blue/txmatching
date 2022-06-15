import { ParsingIssueConfirmationGenerated } from '../generated';
import { ParsingIssueConfirmation } from '../model/ParsingIssueConfirmation';

export const parseParsingIssueConfirmation = (data: ParsingIssueConfirmationGenerated): ParsingIssueConfirmation => {
  return {
    dbId: data.db_id,
    hlaCodeOrGroup: data.hla_code_or_group,
    parsingIssueDetail: data.parsing_issue_detail,
    message: data.message,
    donorId: data.donor_id,
    recipientId: data.recipient_id,
    txmEventId: data.txm_event_id,
    confirmedAt: data.confirmed_at,
    confirmedBy: data.confirmed_by
  };
};
