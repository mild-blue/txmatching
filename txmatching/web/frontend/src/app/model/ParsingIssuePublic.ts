import { ParsingIssuePublicGeneratedParsingIssueDetailEnum } from "@app/generated";

export interface ParsingIssuePublic {
  medicalId: string;
  hlaCodeOrGroup: string;
  message: string;
  parsingIssueDetail: ParsingIssuePublicGeneratedParsingIssueDetailEnum;
  txmEventName: string;
}
