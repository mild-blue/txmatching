export interface ParsingError {
  hlaCodeOrGroup?: string;
  ParsingIssueDetail: string;
  message: string;
  medicalId?: string;
  eventId?: number;
}
