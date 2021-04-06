export interface ParsingError {
  hlaCode: string;
  hlaCodeProcessingResultDetail: string;
  message: string;
  medicalId?: string;
  eventId?: number;
}
