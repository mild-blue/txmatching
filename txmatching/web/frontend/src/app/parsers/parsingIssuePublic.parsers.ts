import { ParsingIssuePublicGenerated } from "../generated";
import { ParsingIssuePublic } from "../model/ParsingIssuePublic";

export const parseParsingIssuePublic = (data: ParsingIssuePublicGenerated): ParsingIssuePublic => {
  return {
    medicalId: data.medical_id,
    hlaCodeOrGroup: data.hla_code_or_group,
    message: data.message,
    parsingIssueDetail: data.parsing_issue_detail,
    txmEventName: data.txm_event_name,
  };
};
