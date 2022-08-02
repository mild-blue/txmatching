export interface ParsingIssue {
  confirmedAt?: string;
  confirmedBy?: number;
  dbId: number;
  donorId?: number;
  hlaCodeOrGroup?: string;
  message: string;
  parsingIssueDetail: string;
  recipientId?: number;
  txmEventId?: number;
}
