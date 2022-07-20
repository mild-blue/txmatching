export interface ParsingIssueConfirmation {
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
