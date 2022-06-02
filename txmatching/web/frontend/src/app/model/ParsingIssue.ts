export interface ParsingIssue {
  hlaCodeOrGroup?: string;
  ParsingIssueDetail: string;
  message: string;
  donorId?: number;
  recipientId?: number;
  eventId?: number;
}
