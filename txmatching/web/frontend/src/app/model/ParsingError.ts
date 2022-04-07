export interface ParsingError {
  hlaCodeOrGroup?: string;
  ParsingIssueDetail: string;
  message: string;
  donorId?: number;
  recipientId?: number;
  eventId?: number;
}
