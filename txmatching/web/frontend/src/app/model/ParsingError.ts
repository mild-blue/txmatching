export interface ParsingError {
  hlaCode: string;
  ParsingIssueDetail: string;
  message: string;
  medicalId?: string;
  eventId?: number;
}
