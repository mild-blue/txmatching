import { ParsingErrorGenerated } from '../generated';
import { ParsingError } from '../model/ParsingError';

export const parseParsingError = (data: ParsingErrorGenerated): ParsingError => {
  return {
    hlaCodeOrGroup: data.hla_code_or_group,
    ParsingIssueDetail: data.parsing_issue_detail,
    message: data.message,
    medicalId: data.medical_id,
    eventId: data.txm_event_id
  };
};
