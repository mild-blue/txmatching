import { ParsingErrorGenerated } from '../generated';
import { ParsingError } from '../model/ParsingError';

export const parseParsingError = (data: ParsingErrorGenerated): ParsingError => {
  return {
    hlaCode: data.hla_code,
    ParsingIssueDetail: data.parsing_issue_detail,
    message: data.message,
    medicalId: data.medical_id,
    eventId: data.txm_event_id
  };
};
