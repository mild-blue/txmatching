export interface ParsingIssueConfirmation {
  confirmed_at?: string;
  confirmed_by?: number;
  db_id: number;
  donor_id?: number;
  hla_code_or_group?: string;
  message: string;
  parsing_issue_detail: string;
  recipient_id?: number;
  txm_event_id?: number;
}
